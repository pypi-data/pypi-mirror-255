import pandas as pd
import numpy as np
from nanoCEM.cem_utils import extract_kmer_feature
import plotnine as p9
from matplotlib import pyplot as plt

plt.rcParams['pdf.fonttype'] = 42

from statsmodels.multivariate.manova import MANOVA
from sklearn.decomposition import PCA
results_path='dna_sample/'
df = pd.read_csv(results_path+'/current_feature.csv')

# 创建PCA对象，并指定降维后的维度
# methylation_list = [
#     2503,1911, 1915,1917, 1939,2498,
#     1835,2552,2030,2604, 2261,746,745,744,1618,2445,
#     2069,1962,955,1594,2580,2457,2605,2501,
# ]
# df = df[df['Position']==2030]
# median_by_group = df.groupby('Group')['Mean'].median()
#
# print(median_by_group)

position=43281378
# position = 43281378

methylation_list=list(range( position- 9 ,position + 10))
i=0
result_list=[]
for item in methylation_list:
    # subsample the reads
    control = df[df['Group']=='Control']
    if control.shape[0] > 10500:
        control=control.iloc[0:10500, :]
    sample = df[df['Group'] == 'Sample']
    if sample.shape[0] > control.shape[0] * 2:
        sample = sample.iloc[0:control.shape[0],:]
    df = pd.concat([control,sample],axis=0).reset_index(drop=True)
    feature,label = extract_kmer_feature(df,3,item)
    y_test = label[0].apply(lambda x: 1 if x == 'Sample' else 0)
    #
    pca = PCA(n_components=2,whiten=True)
    new_df = pd.DataFrame(pca.fit_transform(feature))

    # reducer = umap.UMAP(n_components=2)  # 指定降维后的维度为2
    # new_df = umap.UMAP(
    #     n_neighbors=20,
    #     min_dist=0.0,
    #     n_components=2,
    # ).fit_transform(feature)
    new_df = pd.concat([pd.DataFrame(new_df),label], axis =1)
    new_df.columns=['PC1','PC2','Group']
    if np.sum(new_df['Group']=='Sample') > 10 and np.sum(new_df['Group']=='Control') > 10:
        manova = MANOVA.from_formula('PC1 + PC2 ~ Group', data=new_df)
        # 执行多元方差分析
        results = manova.mv_test()
        pvalue = results.summary().tables[3].iloc[0,5]
        result_list.append([item,pvalue])


new_df = pd.DataFrame(result_list)
new_df[1] = np.log10(new_df[1]) * (-1)
print(i)
new_df.columns=['Position','P value(-log10)']
new_df['Group'] = new_df['P value(-log10)'].apply(lambda x: 'Significant' if x>=2 else 'Not significant')
plot = p9.ggplot(new_df, p9.aes(x='Position', y='P value(-log10)',fill='Group'))\
    + p9.theme_bw() \
    + p9.geom_col() \
    + p9.scale_y_continuous(breaks=[2, 4, 6, 8, 10])\
    + p9.scale_fill_manual(values={'Significant': "#BB9A8B", 'Not significant': "#D7D7DD"}) \
    + p9.geom_hline(yintercept=2,linetype='dashed')\
    + p9.theme(
        figure_size=(8, 3),
        panel_grid_minor=p9.element_blank(),
        axis_text=p9.element_text(size=13),
        axis_title=p9.element_text(size=13),
        title=p9.element_text(size=13),
        legend_position='bottom',
        legend_title=p9.element_blank(),
        strip_text=p9.element_text(size=13),
        strip_background=p9.element_rect(alpha=0),
    )
# plot.save(filename=results_path + "/zscore_density.pdf", dpi=300)
print(plot)
plot.save(filename=results_path + "/pval.pdf", dpi=300)
