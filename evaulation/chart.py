import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('dark_background')
sns.set_style("whitegrid", {
    'axes.grid': True,
    'grid.color': '.3',
    'grid.linestyle': '--',
    'axes.facecolor': '#1a1a1a',
    'figure.facecolor': '#121212'
})
plt.rcParams['figure.figsize'] = (18, 7)
colors = sns.color_palette("husl", 5)

data = [
    {'model': 'Qwen2.5-0.5B-Instruct', 'run': 1, 'elapsed':4.67, 'answer_chars':420, 'pdf_chars':64828, 'cps':89.94, 'thinking': None},
    {'model': 'Qwen2.5-0.5B-Instruct', 'run': 2, 'elapsed':5.89, 'answer_chars':659, 'pdf_chars':77637, 'cps':111.84, 'thinking': None},
    {'model': 'Qwen2.5-0.5B-Instruct', 'run': 3, 'elapsed':6.69, 'answer_chars':722, 'pdf_chars':77642, 'cps':115.40, 'thinking': None},
    {'model': 'Qwen2.5-0.5B-Instruct', 'run': 4, 'elapsed':4.53, 'answer_chars':459, 'pdf_chars':47044, 'cps':101.32, 'thinking': None},
    {'model': 'Qwen2.5-0.5B-Instruct', 'run': 5, 'elapsed':5.62, 'answer_chars':529, 'pdf_chars':52043, 'cps':94.13, 'thinking': None},

    {'model': 'Qwen2.5-1.5B-Instruct', 'run': 1, 'elapsed':16.64, 'answer_chars':527, 'pdf_chars':64828, 'cps':31.67, 'thinking': None},
    {'model': 'Qwen2.5-1.5B-Instruct', 'run': 2, 'elapsed':34.26, 'answer_chars':1258, 'pdf_chars':77637, 'cps':36.72, 'thinking': None},
    {'model': 'Qwen2.5-1.5B-Instruct', 'run': 3, 'elapsed':73.94, 'answer_chars':3131, 'pdf_chars':77642, 'cps':42.35, 'thinking': None},
    {'model': 'Qwen2.5-1.5B-Instruct', 'run': 4, 'elapsed':36.95, 'answer_chars':1604, 'pdf_chars':47044, 'cps':43.41, 'thinking': None},
    {'model': 'Qwen2.5-1.5B-Instruct', 'run': 5, 'elapsed':83.00, 'answer_chars':3256, 'pdf_chars':52043, 'cps':39.23, 'thinking': None},

    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B (thinking included)', 'run': 1, 'elapsed':122.49, 'answer_chars':3190, 'pdf_chars':64828, 'cps':26.04, 'thinking': 'Thinking text included'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B (thinking included)', 'run': 2, 'elapsed':107.41, 'answer_chars':3102, 'pdf_chars':77637, 'cps':28.88, 'thinking': 'Thinking text included'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B (thinking included)', 'run': 3, 'elapsed':124.10, 'answer_chars':4401, 'pdf_chars':77642, 'cps':35.46, 'thinking': 'Thinking text included'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B (thinking included)', 'run': 4, 'elapsed':102.73, 'answer_chars':3279, 'pdf_chars':47044, 'cps':31.92, 'thinking': 'Thinking text included'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B (thinking included)', 'run': 5, 'elapsed':162.91, 'answer_chars':5437, 'pdf_chars':52043, 'cps':33.37, 'thinking': 'Thinking text included'},

    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B', 'run': 1, 'elapsed':122.49, 'answer_chars':601, 'pdf_chars':64828, 'cps':4.9, 'thinking': 'Thinking text excluded'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B', 'run': 2, 'elapsed':107.41, 'answer_chars':1344, 'pdf_chars':77637, 'cps':12.51, 'thinking': 'Thinking text excluded'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B', 'run': 3, 'elapsed':124.10, 'answer_chars':1649, 'pdf_chars':77642, 'cps':13.29, 'thinking': 'Thinking text excluded'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B', 'run': 4, 'elapsed':102.73, 'answer_chars':1626, 'pdf_chars':47044, 'cps':15.83, 'thinking': 'Thinking text excluded'},
    {'model': 'DeepSeek-R1-Distill-Qwen-1.5B', 'run': 5, 'elapsed':162.91, 'answer_chars':1968, 'pdf_chars':52043, 'cps':12.08, 'thinking': 'Thinking text excluded'},
]

df = pd.DataFrame(data)
df['model_type'] = df.apply(lambda x: f"{x['model']} ({x['thinking']})" if x['model'] == 'DeepSeek' else x['model'], axis=1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
fig.patch.set_facecolor('#121212')

barplot = sns.barplot(
    data=df, 
    x='model_type', 
    y='cps', 
    ci=None, 
    ax=ax1, 
    palette=colors, 
    edgecolor='none',
    width=0.7
)
ax1.set_title('Output generation speed comparison\n(Characters per second)', pad=20, color='white', fontsize=14)
ax1.set_xlabel('Model Type', color='white', fontsize=12)
ax1.set_ylabel('Characters per Second', color='white', fontsize=12)
ax1.tick_params(axis='x', rotation=15, colors='white', labelsize=10)
ax1.tick_params(axis='y', colors='white', labelsize=10)
ax1.set_facecolor('#1a1a1a')

for p in barplot.patches:
    height = p.get_height()
    ax1.text(
        p.get_x() + p.get_width()/2., 
        height + 2,
        f'{height:.1f}',
        ha="center", 
        va="bottom", 
        fontsize=10, 
        color='white',
        weight='bold'
    )

scatter = sns.scatterplot(
    data=df, 
    x='answer_chars', 
    y='elapsed', 
    hue='model_type',
    size='pdf_chars', 
    sizes=(50, 300), 
    ax=ax2, 
    palette=colors, 
    edgecolor='none',
    alpha=0.8
)
ax2.set_title('Processing time relative to input and output length\n(Input: PDF length in chars, Output: Answer length in chars)', pad=20, color='white', fontsize=14)
ax2.set_xlabel('Answer Length (characters)', color='white', fontsize=12)
ax2.set_ylabel('Processing Time (seconds)', color='white', fontsize=12)
ax2.tick_params(axis='x', colors='white', labelsize=10)
ax2.tick_params(axis='y', colors='white', labelsize=10)
ax2.set_facecolor('#1a1a1a')

legend = ax2.legend(
    bbox_to_anchor=(1.02, 1), 
    loc='upper left', 
    borderaxespad=0,
    frameon=True,
    facecolor='#1a1a1a',
    edgecolor='#1a1a1a',
    fontsize=10
)
plt.setp(legend.get_texts(), color='white')

plt.tight_layout()
plt.subplots_adjust(wspace=0.3)

plt.show()
