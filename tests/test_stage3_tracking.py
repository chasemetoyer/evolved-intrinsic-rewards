from copy import deepcopy
import pytest
from stage3.tracking import LABEL,TrackioSink,curve_series,panel_html,snapshot_payload


def record(seed=5000,method='E',success=.5,**extra):
    r=dict(method=method,task='DoorKey-8x8',seed=seed,area=success,solved=False,cpu_class='zen3',
           metrics=[{'global_step':2048,'train/success':success,'entropy':.8}]);r.update(extra);return r


def test_task_mean_and_faint_seed_lines_only_use_complete_records():
    p=snapshot_payload([record(success=.2),record(5001,success=.8)],{'limit_usd':'15'})
    ss=curve_series(p['records'],'success');assert [s for s in ss if s['mean']][0]['points']==[(2048,.5)]
    assert len([s for s in ss if s['opacity']<1])==2
    assert p['completed_by_cell']['E/DoorKey-8x8']==2
    assert p['completed_by_cell']['R/UnlockPickup']==0


def test_duplicate_results_rejected_and_missing_telemetry_stays_missing():
    with pytest.raises(ValueError,match='Duplicate'):snapshot_payload([record(),record()],{})
    p=snapshot_payload([record(method='tamper_on')],{})
    assert curve_series(p['records'],'presses_step')==[]
    assert 'No completed-seed telemetry' in panel_html(p)['tamper/presses per step']


def test_every_required_panel_has_progress_label_and_intrinsic_reference():
    r=record(method='tamper_on');r['metrics'][0].update({'tamper/presses_per_step':.25,'train/tampers':2.,'train/int_ret':.6})
    p=snapshot_payload([r],{'guard_total_usd':'1.25','limit_usd':'15'})
    panels=panel_html(p)
    assert len(panels)==18
    assert all(LABEL in v for v in panels.values())
    assert 'P0 = 0.64' in panels['tamper/intrinsic episode return']
    assert all('learning/'+t in panels for t in ('DoorKey-8x8','UnlockPickup','KeyCorridorS3R2'))


class Client:
    def __init__(self,fail=False):self.fail=fail;self.kwargs=None;self.logged=None
    def init(self,**kwargs):self.kwargs=kwargs;return self
    def Html(self,doc,caption):return {'doc':doc,'caption':caption}
    def log(self,metrics,step):
        if self.fail:raise RuntimeError('credential=SECRET must not escape')
        self.logged=(metrics,step)
    def finish(self):pass


def environment():return {'TRACKIO_PROJECT':'evolved-intrinsic-rewards','ORX_RUN_ID':'smoke-run','ORX_EXPERIMENT':'stage3','TRACKIO_SPACE_ID':'owner/private-space'}


def test_native_visualize_identity_and_private_remote_logging_without_mutating_inputs():
    p=snapshot_payload([record()],{'limit_usd':'15'});before=deepcopy(p);c=Client();sink=TrackioSink(environ=environment(),client=c)
    assert sink.publish(p,7)['ok']
    assert c.kwargs['name']=='smoke-run' and c.kwargs['group']=='stage3' and c.kwargs['private'] is True
    assert c.kwargs['embed'] is False and c.kwargs['resume']=='allow'
    assert c.logged[1]==7 and len(c.logged[0])>18 and p==before


def test_tracking_failure_cannot_raise_or_expose_credentials():
    p=snapshot_payload([],{});sink=TrackioSink(environ=environment(),client=Client(fail=True))
    result=sink.publish(p,1);assert result=={'ok':False,'error_type':'RuntimeError','step':1}
    assert 'SECRET' not in str(result)


@pytest.mark.parametrize('env',[{},dict(environment(),TRACKIO_SPACE_ID='',TRACKIO_SERVER_URL='http://localhost:7860')])
def test_no_local_fallback_when_remote_is_unconfigured(env):
    assert TrackioSink(environ=env,client=Client()).publish(snapshot_payload([],{}),0)['ok'] is False


def test_private_prefix_gates_all_reads_and_writes_and_keeps_rootpath():
    import asyncio
    import httpx
    from stage3.tracking_server import CapabilityPrefix
    calls=[];commits=[]
    async def app(scope,receive,send):
        calls.append(scope)
        await send({'type':'http.response.start','status':200,'headers':[]})
        await send({'type':'http.response.body','body':b'ok'})
    token='x'*48
    wrapped=CapabilityPrefix(app,token,after_write=lambda:commits.append(True))
    async def test():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=wrapped),base_url='https://test') as c:
            for path in ['/','/api/project','/file?path=/tracking/data','/private/'+token+'-extra/api/project']:
                assert (await c.get(path)).status_code==404
            assert (await c.get('/private/'+token+'/api/project')).status_code==200
            assert calls[-1]['path']=='/api/project' and calls[-1]['root_path']=='/private/'+token
            assert not commits
            assert (await c.post('/private/'+token+'/api/log')).status_code==200
            assert commits==[True]
    asyncio.run(test())


def test_private_server_refuses_empty_or_short_read_credentials():
    from stage3.tracking_server import CapabilityPrefix
    with pytest.raises(ValueError):CapabilityPrefix(None,'')
    with pytest.raises(ValueError):CapabilityPrefix(None,'short')


def test_library_stdout_and_stderr_cannot_echo_private_endpoint(capsys,caplog):
    import sys
    class Noisy(Client):
        def init(self,**kwargs):
            print('https://host/private/SECRET');print('SECRET',file=sys.stderr)
            return super().init(**kwargs)
        def log(self,metrics,step):
            import logging
            logging.warning('https://host/private/SECRET')
            print('SECRET');return super().log(metrics,step)
        def finish(self):print('SECRET')
    sink=TrackioSink(environ=environment(),client=Noisy())
    assert sink.publish(snapshot_payload([],{}),0)['ok'];assert sink.finish()['ok']
    output=capsys.readouterr();assert 'SECRET' not in output.out+output.err+caplog.text


def test_modal_server_factory_declares_serializable_singleton_without_launch(monkeypatch):
    import modal
    from stage3.tracking_server import APP_NAME,VOLUME_NAME,make_tracking_app
    monkeypatch.setenv('TRACKIO_ACCESS_PATH_TOKEN','fixture'*8)
    monkeypatch.setenv('TRACKIO_WRITE_TOKEN','fixture'*8)
    app,function,volume=make_tracking_app(modal.Image.debian_slim())
    assert app.name==APP_NAME and volume.name==VOLUME_NAME
    assert function is not None  # Definition construction catches unsupported local-function closures.
