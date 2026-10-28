# Amendment 20261026T192733Z (UTC)

Written before any round-4 training run had finished. At this time the first run (A1a) was still in progress and
no round-4 result had been read. Pre-registration sha256 79fdfed000d5e6f892d9201cadd970808cf3b0949e4b3e3d925be9839800faa1
is unchanged.

1. **Ties in Mann-Whitney tests.** The pre-registration says "exact, one-sided". The exact null distribution in
   scipy assumes no ties, and ties are expected: first-solved steps censored at 2,000,000, and evaluation-curve
   areas of exactly 0 or 1.
   - When the two samples have no tied values, the exact method is used.
   - When ties exist, a permutation test of the same U statistic is used: 200,000 random relabelings, seed 0,
     one-sided in the pre-registered direction.
   - The report states which method each test used.
2. **Holm set.** "All significance-tested predictions" means the tests that decide a hit. That is 17 tests:
   - A1-P1, A1-P2;
   - A2-P1 to A2-P8;
   - PB2 (4 tests);
   - PB3 (2 tests);
   - PB4.

   The binomial tests for PB1 and PB5, and the MWU tests reported under A1-P3 and A1-P4, are descriptive. Their
   hits are decided by range or by median ordering, so they are reported with raw p only.
