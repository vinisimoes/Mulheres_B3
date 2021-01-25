import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import transforms
from matplotlib.offsetbox import TextArea, VPacker, AnnotationBbox


def get_data_from_website():
    driver = webdriver.Chrome()
    driver.get("https://comoinvestir.thecap.com.br/participacao-mulheres-na-bolsa-de-valores-b3/")

    delay = 15  # seconds
    try:
        nao_btn = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.ID, 'onesignal-slidedown-cancel-button')))
        nao_btn.click()

        close_btn = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="om-epedjhuhczktsayvzn5k-optin"]/div/button')))
        close_btn.click()
    except TimeoutException:
        pass

    num_rows = len(driver.find_elements_by_xpath("//*[@id=\"post-52791\"]/div[5]/div[6]/table/tbody/tr"))
    num_cols = len(driver.find_elements_by_xpath("//*[@id=\"post-52791\"]/div[5]/div[6]/table/tbody/tr[4]/td"))

    before_XPath = '//*[@id="post-52791"]/div[5]/div[6]/table/tbody/tr['
    aftertr_XPath = ']/td['
    aftertd_XPath = ']'

    data_list = []
    driver.implicitly_wait(10)
    for t_row in range(4, (num_rows + 1)):
        row_list = []
        for t_column in range(1, (num_cols + 1)):
            FinalXPath = before_XPath + str(t_row) + aftertr_XPath + str(t_column) + aftertd_XPath
            cell_text = driver.find_element_by_xpath(FinalXPath).text
            row_list.append(cell_text)
        data_list.append(row_list)

    data_df = pd.DataFrame(data_list,
                           columns=['ano', 'qtd_homens', 'pct_homens', 'qtd_mulheres', 'pct_mulheres', 'total'])
    data_df = data_df[1:]
    data_df.to_csv('mulheres_data_str.csv', index=False)


def get_formated_data():
    data = pd.read_csv('mulheres_data_str.csv', dtype=object)

    data['ano'] = data['ano'].map(lambda x: int(x))
    data['qtd_homens'] = data['qtd_homens'].map(lambda x: int(x.replace('.', '')))
    data['pct_homens'] = data['pct_homens'].map(lambda x: float(x[:-1].replace(',', '.')))
    data['qtd_mulheres'] = data['qtd_mulheres'].map(lambda x: int(x.replace('.', '')))
    data['pct_mulheres'] = data['pct_mulheres'].map(lambda x: float(x[:-1].replace(',', '.')))
    data['total'] = data['total'].map(lambda x: int(x.replace('.', '')))

    return data


if __name__ == '__main__':
    # get_data_from_website()
    data_df = get_formated_data()

    # get useful lists to plot
    ano = data_df['ano'].tolist()
    qtd_mulheres = data_df['qtd_mulheres'].to_numpy() / 1000000
    qtd_homens = data_df['qtd_homens'].to_numpy() / 1000000
    pct_mulheres = data_df['pct_mulheres'].to_numpy()

    qtd_anos = len(ano)

    # define colors
    GRAY1, GRAY2, GRAY3 = '#231F20', '#414040', '#555655'
    GRAY4, GRAY5, GRAY6 = '#646369', '#76787B', '#828282'
    GRAY7, GRAY8, GRAY9 = '#929497', '#A6A6A5', '#BFBEBE'
    BLUE1, BLUE2, BLUE3, BLUE4 = '#174A7E', '#4A81BF', '#94B2D7', '#94AFC5'
    RED1, RED2 = '#C3514E', '#E6BAB7'
    GREEN1, GREEN2 = '#0C8040', '#9ABB59'
    ORANGE1 = '#F79747'

    # configure plot font family to Arial
    plt.rcParams['font.family'] = 'Arial'
    # configure mathtext bold and italic font family to Arial
    matplotlib.rcParams['mathtext.fontset'] = 'custom'
    matplotlib.rcParams['mathtext.bf'] = 'Arial:bold'
    matplotlib.rcParams['mathtext.it'] = 'Arial:italic'

    # create new figure
    fig, axes = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]}, figsize=(10, 5), dpi=110)
    fig.suptitle('Quantidade de mulheres na bolsa de valores', color=GRAY4, fontsize=17, fontweight='bold')

    # grid the graph
    axes[1].set_axisbelow(True)
    axes[1].grid(color=GRAY8, ls='-.', lw=0.25)

    # plot actual data
    # draw processed tickets line with markers
    axes[0].plot(range(qtd_anos), pct_mulheres, linewidth=2, color=RED1)
    axes[0].scatter(range(qtd_anos), pct_mulheres, s=20, color=RED1, clip_on=False)
    # annotate received
    for i, v in enumerate(pct_mulheres):
        axes[0].annotate(str(v)+'%',
                         (i, v),  # (x,y) point to annotate
                         xytext=(-10, -16),  # (x,y) to place the text at
                         textcoords='offset points',  # offset (in points)
                         color=RED1,
                         fontsize=7)

    axes[1].bar(list(range(qtd_anos)), qtd_mulheres, width=0.68, color=RED1,
                edgecolor='white', linewidth=0.9)
    axes[1].bar(list(range(qtd_anos)), qtd_homens, width=0.68, bottom=qtd_mulheres, color=GRAY8,
                edgecolor='white', linewidth=0.9)

    # set properties for axes object (ticks for all issues with labels)
    plt.setp(axes[0], xticks=list(range(0, qtd_anos)), xticklabels="")
    axes[0].tick_params(axis=u'both', which=u'both', length=0)

    plt.setp(axes[1], xticks=list(range(0, qtd_anos)), xticklabels=ano)
    plt.xticks(rotation=45)
    axes[1].tick_params(axis=u'both', which=u'both', length=0)

    # remove chart border
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)
    axes[0].spines['bottom'].set_visible(False)
    axes[0].spines['left'].set_color(GRAY9)
    axes[0].spines['left'].set_linewidth(1.5)

    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)
    axes[1].spines['bottom'].set_color(GRAY9)
    axes[1].spines['left'].set_color(GRAY9)
    axes[1].spines['left'].set_linewidth(1.5)
    axes[1].spines['bottom'].set_linewidth(1.5)

    # configure x tick label appearance
    for item in axes[1].get_xticklabels():
        item.set_fontsize(10)
        item.set_color(GRAY4)
        # use trasformations to shift x tick labels slightly down
        offset = transforms.ScaledTranslation(0, -0.07, fig.dpi_scale_trans)
        item.set_transform(item.get_transform() + offset)

    # configure y tick label appearance
    for item in axes[0].get_yticklabels():
        item.set_fontsize(10)
        item.set_color(GRAY7)
        # use trasformations to shift y tick labels slightly left
        offset = transforms.ScaledTranslation(-0.07, 0, fig.dpi_scale_trans)
        item.set_transform(item.get_transform() + offset)

    for item in axes[1].get_yticklabels():
        item.set_fontsize(10)
        item.set_color(GRAY7)
        # use trasformations to shift y tick labels slightly left
        offset = transforms.ScaledTranslation(-0.07, 0, fig.dpi_scale_trans)
        item.set_transform(item.get_transform() + offset)

    # place a text box in upper left in axes coords
    # texts = ['Homens', 'Mulheres']
    # colors = [GRAY4, RED1]
    # Texts = []
    # for t, c in zip(texts, colors):
    #     Texts.append(TextArea(t, textprops=dict(color=c)))
    # texts_vbox = VPacker(children=Texts, pad=0, sep=0)
    # ann = AnnotationBbox(texts_vbox, (.05, 0.81), xycoords=axes[1].transAxes,
    #                      box_alignment=(0, .5), bboxprops=dict(color=GRAY4, facecolor='white',
    #                                                            boxstyle='round'))
    # ann.set_figure(fig)
    # fig.artists.append(ann)

    # label colors
    axes[1].text(0.97, 0.55, 'Homens', transform=axes[1].transAxes, fontsize=13, color=GRAY6, fontweight='bold')
    axes[1].text(0.97, 0.1, 'Mulheres', transform=axes[1].transAxes, fontsize=13, color=RED1, fontweight='bold')

    # title the axis
    axes[0].text(-0.08, 0.0, 'Percentual (%)', transform=axes[0].transAxes, fontsize=14, rotation='vertical',
                 color=GRAY4)
    axes[1].text(-0.08, 0.35, 'Milhões', transform=axes[1].transAxes, fontsize=14, rotation='vertical',
                 color=GRAY4)

    plt.show()
