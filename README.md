RADio
================

-   <a href="#computing-radio-with-rank-aware-js-divergence"
    id="toc-computing-radio-with-rank-aware-js-divergence">1 Computing RADio
    with rank-aware JS-divergence</a>
-   <a href="#from-scratch" id="toc-from-scratch">2 from scratch</a>
-   <a href="#additional-material" id="toc-additional-material">3 Additional
    Material</a>
    -   <a href="#jensen-shannon-as-an-f-divergence"
        id="toc-jensen-shannon-as-an-f-divergence">3.1 Jensen Shannon as an
        f-Divergence</a>
    -   <a href="#radio-with-kl-divergence"
        id="toc-radio-with-kl-divergence">3.2 RADio with KL divergence</a>
    -   <a
        href="#jensen-shannon-divergence-kullback-leibler-divergence-with-and-without-rank-awareness"
        id="toc-jensen-shannon-divergence-kullback-leibler-divergence-with-and-without-rank-awareness">3.3
        Jensen-Shannon divergence Kullback-Leibler divergence with and without
        rank-awareness</a>
    -   <a
        href="#jensen-shannon-divergence-for-all-recommender-strategies-without-cutoff"
        id="toc-jensen-shannon-divergence-for-all-recommender-strategies-without-cutoff">3.4
        Jensen-Shannon divergence for all recommender strategies without
        cutoff</a>

This repository contains the supporting material for the paper 📻 *RADio
– Rank-Aware Divergence metrIcs to measure nOrmative diversity in news
recommendations*.

# 1 Computing RADio with rank-aware JS-divergence

1.  download `articles_large.pickle`:
    <https://drive.google.com/file/d/1XgXetSxweN9rLo6vCMMR5ur5lvYWJYCY/view?usp=sharing>
2.  download `recommendations_large_all_recs_no_cap.pickle`:
    <https://drive.google.com/file/d/17X9fkhBxzNhHhWgb_XHQJ1WVexhnsZnX/view?usp=sharing>
3.  Put `articles_large.pickle` and
    `recommendations_large_all_recs_no_cap.pickle` in the data folder
4.  download `behaviors_large.tsv`:
    <https://drive.google.com/file/d/13ENNPX7f7Qb2vLtdp94Zo5lBflch_hiJ/view?usp=sharing>
5.  Put `behaviors_large.tsv` in the data/recommendations folder

<!-- -->

    git clone https://github.com/svrijenhoek/RADio.git
    pip install -r requirements.txt
    python metrics_calculation.py

# 2 from scratch

MacOS

    brew tap elastic/tap
    brew install elastic/tap/elasticsearch-full

    python -m spacy download en_core_web_sm

# 3 Additional Material

## 3.1 Jensen Shannon as an f-Divergence

![](viz/figs/JSasF.jpg)<!-- -->

## 3.2 RADio with KL divergence

<table>
<caption>
RADio framework with DART metrics based on KL divergence with
recommendation algorithms on the MIND dataset. From left to right:
Calibration (topic), Calibration (complexity), Fragmentation,
Activation, Representation and Alternative Voices. These metrics are
executed on a random sample of 35.000 users, with rank-awareness, and
without cutoff point.
</caption>
<thead>
<tr>
<th style="text-align:left;">
rec_type
</th>
<th style="text-align:right;">
calibration_topic
</th>
<th style="text-align:right;">
calibration_complexity
</th>
<th style="text-align:right;">
fragmentation
</th>
<th style="text-align:right;">
affect
</th>
<th style="text-align:right;">
representation
</th>
<th style="text-align:right;">
alternative_voices
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
lstur
</td>
<td style="text-align:right;">
2.6038
</td>
<td style="text-align:right;">
1.1432
</td>
<td style="text-align:right;">
7.7201
</td>
<td style="text-align:right;">
0.1481
</td>
<td style="text-align:right;">
0.1078
</td>
<td style="text-align:right;">
0.0142
</td>
</tr>
<tr>
<td style="text-align:left;">
naml
</td>
<td style="text-align:right;">
2.5333
</td>
<td style="text-align:right;">
1.1287
</td>
<td style="text-align:right;">
7.3926
</td>
<td style="text-align:right;">
0.1531
</td>
<td style="text-align:right;">
0.1047
</td>
<td style="text-align:right;">
0.0127
</td>
</tr>
<tr>
<td style="text-align:left;">
npa
</td>
<td style="text-align:right;">
2.5945
</td>
<td style="text-align:right;">
1.1390
</td>
<td style="text-align:right;">
7.6202
</td>
<td style="text-align:right;">
0.1521
</td>
<td style="text-align:right;">
0.1237
</td>
<td style="text-align:right;">
0.0134
</td>
</tr>
<tr>
<td style="text-align:left;">
nrms
</td>
<td style="text-align:right;">
2.5013
</td>
<td style="text-align:right;">
1.1204
</td>
<td style="text-align:right;">
7.4519
</td>
<td style="text-align:right;">
0.1442
</td>
<td style="text-align:right;">
0.1114
</td>
<td style="text-align:right;">
0.0113
</td>
</tr>
<tr>
<td style="text-align:left;">
pop
</td>
<td style="text-align:right;">
2.9384
</td>
<td style="text-align:right;">
1.1082
</td>
<td style="text-align:right;">
7.6377
</td>
<td style="text-align:right;">
0.1605
</td>
<td style="text-align:right;">
0.1028
</td>
<td style="text-align:right;">
0.0102
</td>
</tr>
<tr>
<td style="text-align:left;">
random
</td>
<td style="text-align:right;">
3.6038
</td>
<td style="text-align:right;">
1.5985
</td>
<td style="text-align:right;">
8.6295
</td>
<td style="text-align:right;">
0.8079
</td>
<td style="text-align:right;">
1.1248
</td>
<td style="text-align:right;">
0.0420
</td>
</tr>
</tbody>
</table>

## 3.3 Jensen-Shannon divergence Kullback-Leibler divergence with and without rank-awareness

![Jensen-Shannon divergence for each DART metric, with and without
rank-awareness, with a cutoff @10. Boxplot with median and the
interquartile range in the inner box.](viz/figs/KL.jpg)

![Kullback-Leibler divergence for each DART metric, with and without
rank-awareness, with a cutoff @10. Boxplot with median and the
interquartile range in the inner box.](viz/figs/JS.jpg)

## 3.4 Jensen-Shannon divergence for all recommender strategies without cutoff

![Jensen-Shannon divergence for each DART metric for all neural
recommender strategies, with and without rank-awareness, and without a
cutoff. Without rank-awareness and cutoff no divergence is found for the
Activation, Representation and Alternative Voices metrics, as in these
cases the recommendation and the context are identical. Boxplot with
median and the interquartile range in the inner
box.](viz/figs/boxplot_full.jpg)
