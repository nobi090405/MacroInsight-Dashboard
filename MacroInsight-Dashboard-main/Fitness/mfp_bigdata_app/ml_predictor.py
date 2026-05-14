import datetime
import pandas as pd
import plotly.express as px
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression as SparkLinearRegression

def run_spark_prediction(df_user, spark):
    if len(df_user) <= 3:
        return None, "No hay suficientes días registrados para este usuario para hacer una predicción fiable."

    # 1. Preparar datos
    df_user['date_ordinal'] = df_user['date'].map(datetime.datetime.toordinal)
    pdf_subset = df_user[['date_ordinal', 'total_kcal']].copy()
    spark_df = spark.createDataFrame(pdf_subset)
    
    # 2. Ensamblar y renombrar
    assembler = VectorAssembler(inputCols=['date_ordinal'], outputCol='features')
    spark_df_assembled = assembler.transform(spark_df)
    spark_df_final = spark_df_assembled.withColumnRenamed('total_kcal', 'label')
    
    # 3. Entrenar el modelo
    lr_spark = SparkLinearRegression(featuresCol='features', labelCol='label')
    model_spark = lr_spark.fit(spark_df_final)
    
    # 4. Fechas futuras
    last_date = df_user['date'].max()
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, 8)]
    future_ordinal = [d.toordinal() for d in future_dates]
    
    # 5. Predecir
    future_pdf = pd.DataFrame({'date_ordinal': future_ordinal})
    spark_future = spark.createDataFrame(future_pdf)
    spark_future_assembled = assembler.transform(spark_future)
    predictions = model_spark.transform(spark_future_assembled)
    
    # 6. Preparar datos para gráfica
    preds_pd = predictions.select('prediction').toPandas()
    df_future = pd.DataFrame({
        'date': future_dates, 
        'Predicción Kcal': preds_pd['prediction']
    })
    
    # 7. Crear Gráfico
    fig_pred = px.line(df_user, x='date', y='total_kcal', title="Historial vs Predicción Distribuida (Spark) a 7 Días")
    fig_pred.add_scatter(x=df_future['date'], y=df_future['Predicción Kcal'], mode='lines+markers', name='Tendencia Proyectada', line=dict(dash='dash', color='red'))
    
    rmse = model_spark.summary.rootMeanSquaredError
    
    return fig_pred, rmse