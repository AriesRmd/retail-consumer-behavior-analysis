# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "duckdb>=1.4.3",
#     "marimo>=0.19.0",
#     "numpy>=2.4.1",
#     "pandas>=2.3.3",
#     "plotly>=6.5.2",
#     "pyzmq>=27.1.0",
#     "sqlglot>=28.6.0",
# ]
# ///

import marimo

__generated_with = "0.19.5"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    slider = mo.ui.slider(1, 100)
    import pandas as pd
    import numpy as np

    # Memuat dataset dari folder data
    # Ganti 'nama_file.csv' dengan nama file asli di folder data kamu
    file_path = r'D:\Workspace Aries\PROJECT\retail-consumer-behavior-analysis\data\customer_shopping_behavior.csv'
    df= pd.read_csv(file_path)
    return df, mo, pd


@app.cell
def _(df):
    # Melihat 5 baris pertama untuk memahami struktur data
    print("Preview Data:")
    df.head()
    return


@app.cell
def _(df):
    # Mengecek informasi dasar (tipe data dan missing values)
    print("\nData Info:")
    df.info()
    return


@app.cell
def _(df):
    df.describe()
    return


@app.cell
def _(mo):
    mo.md(r"""
    Loyalitas (Previous Purchases)
    * Tingkat Retensi: Ini adalah kolom paling menarik. Rata-rata pelanggan sudah melakukan 25 kali pembelian sebelumnya.
    * Loyalitas Tinggi: Sebanyak 25% pelanggan (Q3) tercatat sudah melakukan pembelian antara 38 hingga 50 kali. Ini adalah segmen "Loyal" yang sangat berharga bagi perusahaan.
    * Pelanggan Baru: Nilai minimum 1 menunjukkan ada pelanggan yang baru pertama kali berbelanja.

    ***Kesimpulan untuk Analisis:***
    Dari data ini, kita bisa menyimpulkan bahwa perusahaan memiliki basis pelanggan yang sangat setia (dilihat dari tingginya angka Previous Purchases), namun perlu strategi untuk meningkatkan nilai rata-rata transaksi agar bisa melewati angka $60 dan memperbaiki rating agar mencapai angka 4.0.
    """)
    return


@app.cell
def _(df):
    # Menampilkan nilai unik untuk tipe kolom bertipe data 'Object'

    for i in df.columns:
      if df[i].dtype == 'O':
        print("========{}========".format(i))
        print(df[i].unique())
        print("")
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Missing Value**
    """)
    return


@app.cell
def _(df, pd):
    def missing_check(df):
        missing = df.isnull().sum()
        percent = 100*(missing/len(df))
        number_unique = df.nunique()
        data_type = df.dtypes
        return pd.DataFrame({"Missing":missing,
                              "Percent_Missing":percent,
                              "Number_Unique":number_unique,
                              "Data_Types":data_type}).sort_values("Percent_Missing")

    # check missing value
    missing_check(df)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Perhatikan review rating. Artinya, ada 37 pelanggan yang tidak memberikan rating. Maka dari itu missing value akan ditangani terlebih dahulu menggunakan median dengan category sebagai kolom pembantu. Jika hanya mean takutnya jika ada outlier akan menghasilkan bias. Terlebih lagi, melakukan imputasi berdasarkan kategori (seperti kategori produk atau kelompok usia) akan membuat data jauh lebih akurat.

    Misalnya, produk di kategori Clothing mungkin secara umum punya rating yang berbeda dengan Electronics. Mengisi rating yang kosong dengan nilai tengah dari kategori yang sama akan menjaga integritas data.
    """)
    return


@app.cell
def _(df):
    # Mengisi missing value pada 'Review Rating' dengan median berdasarkan kategori produk
    # Asumsi kolom kategori produk bernama 'Category' (sesuaikan dengan nama kolom aslimu)

    df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(
        lambda x: x.fillna(x.median())
    )

    # Cek apakah sudah terisi semua
    print(f"Jumlah missing value setelah imputasi: {df['Review Rating'].isnull().sum()}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    **Feature Engineering (Modeling)**

    * Agar analisis di SQL dan Power BI nanti lebih tajam, kita perlu membuat kolom baru (fitur) berdasarkan statistik yang ada:

    * Age Grouping: Berdasarkan statistik, usia konsumen berkisar antara 18 hingga 70 tahun. Kita bisa membaginya menjadi kategori seperti 'Teen', 'Adult', dan 'Senior'.

    * Customer Segmentation (Loyalty): Kolom Previous Purchases menunjukkan angka dari 1 hingga 50. Kita bisa membuat kategori 'New Customer' (pembelian rendah) dan 'Loyal Customer' (pembelian tinggi).
    """)
    return


@app.cell
def _(df):
    # Membuat fungsi untuk pengelompokan usia
    def age_categorizer(age):
        if age <= 25:
            return 'Gen Z'
        elif age <= 40:
            return 'Millennials'
        elif age <= 55:
            return 'Gen X'
        else:
            return 'Seniors'

    # Menerapkan fungsi ke kolom baru
    df['Age Group'] = df['Age'].apply(age_categorizer)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Karena kita punya Previous Purchases dan Frequency of Purchases, kita bisa membuat profil loyalitas yang lebih kuat.

    * Loyalty Level: Menggabungkan jumlah pembelian masa lalu.
    * Shopping Habit: Mengkategorikan seberapa sering mereka belanja.
    """)
    return


@app.cell
def _(df):
    # Segmentasi Pelanggan (RFM-ish Approach)
    # Kolom: 'Frequency of Purchases' (e.g., Weekly, Fortnightly, Monthly, etc.)
    df['Purchase_Frequency_Days'] = df['Frequency of Purchases'].map({
        'Weekly': 7, 
        'Fortnightly': 14, 
        'Monthly': 30, 
        'Every 3 Months': 90, 
        'Annually': 365,
        'Bi-Weekly':14,
        'Quarterly':90
    })
    return


@app.cell
def _(df):
    df.head()
    return


@app.cell
def _(mo):
    mo.md(r"""
    Analisis Sensitivitas Promo (Sangat Penting untuk Strategi)

    Menggunakan kolom Discount Applied dan Promo Code Used untuk melihat apakah seorang pelanggan adalah "Pemburu Diskon".
    * Is_Promo_User: Jika Discount Applied adalah 'Yes', maka pelanggan tersebut dipicu oleh promo.
    """)
    return


@app.cell
def _(df):
    # Checking apakah semua diskon mempunyai promo code
    # Biasanya ada diskon yang tidak mempunyai kode promo seperti tanggal kembar
    (df['Discount Applied'] == df['Promo Code Used']).all()

    # True = semua ada promo code
    return


@app.cell
def _(df):
    df.columns
    return


@app.cell
def _(df):
    # Ganti 'df' dengan nama DataFrame kamu
    df2 = df.rename(columns={
        'Customer ID':'customer_id',
        'Category':'category',
        'Location':'location',
        'Size':'size',
        'Color':'color',
        'Season':'season',
        'Promo Code Used':'promo_code_used',
        'Payment Method':'payment_method',
        'Prequency of Purchases':'prequency_purchase',
        'Age Group':'age_group',
        'Purchase_Frequency_Days':'purchase_prequency_days',
        'Purchase Amount (USD)': 'revenue',
        'Review Rating': 'rating',
        'Shipping Type': 'shipping',
        'Discount Applied': 'has_discount',
        'Gender': 'gender',
        'Age': 'age',
        'Item Purchased': 'product_name',
        'Previous Purchases': 'total_orders',
        'Subscription Status': 'is_subscriber'
    }).convert_dtypes()
    return (df2,)


@app.cell
def _(df2):
    df2.info()
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Question
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        select *
        from df2
        limit 5
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q1: Total revenue by Gender (Male vs Female)
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SELECT gender, sum(revenue) as Revenue
        from df2
        group by 1
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q2: Customers with discount who spent more than average
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        select customer_id,revenue,location,age_group
        from df2
        where has_discount ='Yes' and revenue > (select avg(revenue) from df2)
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q3: Top 5 products with highest average review rating
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        select product_name, avg(rating) as rating_average
        from df2
        group by 1
        order by 2 desc
        limit 5
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q4: Average Purchase Amount: Standard vs Express Shipping
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        select shipping, avg(revenue)
        from df2
        where shipping in ('Standard','Express')
        group by 1
        order by 2 desc
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q5: Revenue contribution by age group
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SELECT age_group, sum(revenue)
        FROM df2
        GROUP BY 1
        ORDER BY 2 desc
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q6: Compare Average Spending & Total Revenue Between Subscriber and Non-Sub
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        select is_subscriber, sum(total_orders) as total_order,sum(revenue) as total_revenue
        from df2
        group by 1
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q7: Which 5 Product have the highest percentage of purchase with discount applied
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        select 
        product_name, 
        (sum(revenue)/(select sum(revenue) from df2))*100 as percentage_of_purchased_discount
        from df2
        where has_discount = 'Yes'
        group by 1
        order by 2 desc
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q8: Top 3 revenue di setiap kategori
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        with rev_rank as(
            select 
                category, 
                product_name,
                sum(revenue) as revenue,
                rank() over (partition BY category order by sum(revenue) desc)as ranking
            from df2
            group by 1,2
        )
        select *
        from rev_rank
        where ranking <=3
        order by 1
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Python Version
    """)
    return


@app.cell
def _(df2):
    # 1. Agregasi: Hitung total revenue per kategori dan per produk
    # Kita reset_index agar data kembali menjadi tabel (DataFrame)
    df_revenue = df2.groupby(['category', 'product_name'])['revenue'].sum().reset_index()

    # 2. Ambil Top 3: Gunakan nlargest di dalam grup kategori
    top_3_revenue = (
        df_revenue.groupby('category')
        .apply(lambda x: x.nlargest(3, 'revenue'), include_groups=False)
        .reset_index()
    )

    # 3. Opsional: Hapus kolom 'level_1' yang muncul akibat reset_index pada apply
    top_3_revenue = top_3_revenue.drop(columns=['level_1'], errors='ignore')

    top_3_revenue
    return


@app.cell
def _(mo):
    mo.md(r"""
    Q9: are customer who are repeat buyers (more than 5 previous purchase) also likely to subscribe
    """)
    return


@app.cell
def _(df2):
    # 1. Tandai pelanggan: True jika > 5, False jika <= 5
    df2['is_repeat_buyer'] = df2['total_orders'] > 5

    # 2. Hitung persentase langganan di tiap grup
    # Misal kolom status langganan bernama 'is_subscriber' dengan nilai 'Yes'/'No'
    subscription_analysis = df2.groupby('is_repeat_buyer')['is_subscriber'].value_counts(normalize=True).unstack() * 100

    subscription_analysis
    return


@app.cell
def _(df2, mo):
    import plotly.express as px

    # Menyiapkan data untuk grafik
    plot_data = df2.groupby(['is_repeat_buyer', 'is_subscriber']).size().reset_index(name='count')

    fig = px.bar(
        plot_data, 
        x='is_repeat_buyer', 
        y='count', 
        color='is_subscriber',
        barmode='group',
        labels={'is_repeat_buyer': 'Repeat Buyer (>5 Purchases)', 'count': 'Jumlah Customer'},
        title='Perbandingan Langganan: Repeat Buyer vs Reguler'
    )

    mo.ui.plotly(fig)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
