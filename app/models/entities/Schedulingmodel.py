from app.utils.DateFormat import DateFormat

class Schedule():
    def __init__(
            self,
            nb_clase_id=None, 
            tb_gimnasio_id=None, 
            df_fecha=None, 
            df_hora=None,
            tb_calificacion_id = None,
            ) -> None:
        self.nb_clase_id = nb_clase_id
        self.tb_gimnasio_id = tb_gimnasio_id
        self.df_fecha = df_fecha
        self.df_hora = df_hora
        self.tb_calificacion_id = tb_calificacion_id
    
    def to_JSON(self):
        formatted_date = None
        if self.df_fecha is not None:
            formatted_date = DateFormat.convert_date(self.df_fecha)
        return {
            'nb_clase_id': self.nb_clase_id,
            'tb_gimnasio_id': self.tb_gimnasio_id,
            'df_fecha': formatted_date,
            'df_hora': self.df_hora,
            'tb_calificacion_id': self.tb_calificacion_id
        }