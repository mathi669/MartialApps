from app.utils.DateFormat import DateFormat

class CreateNewClass():
    def __init__(
            self,
            dc_horario=None, 
            nb_cupos_disponibles=None, 
            id_categoria=None,
            df_fecha=None,
            df_hora=None,
            tb_clase_estado_id = None,
            tb_gimnasio_id = None,
            tb_arte_marcial_id = None,
            tb_profesor_id = None,
            dc_nombre_clase = None,
            dc_imagen_url = None,
            ) -> None:
        self.dc_horario = dc_horario
        self.nb_cupos_disponibles = nb_cupos_disponibles
        self.id_categoria = id_categoria
        self.df_fecha = df_fecha
        self.df_hora = df_hora
        self.tb_clase_estado_id = tb_clase_estado_id
        self.tb_gimnasio_id = tb_gimnasio_id
        self.tb_arte_marcial_id = tb_arte_marcial_id
        self.tb_profesor_id = tb_profesor_id
        self.dc_nombre_clase = dc_nombre_clase
        self.dc_imagen_url = dc_imagen_url
        
    
    def to_JSON(self):
        formatted_date = None
        if self.df_fecha is not None:
            formatted_date = DateFormat.convert_date(self.df_fecha)
        return {
            'dc_horario': self.dc_horario,
            'nb_cupos_disponibles': self.nb_cupos_disponibles,
            'id_categoria': self.id_categoria,
            'df_fecha': formatted_date,
            'df_hora': self.df_hora,
            'tb_clase_estado_id': self.tb_clase_estado_id,
            'tb_gimnasio_id': self.tb_gimnasio_id,
            'tb_profesor_id': self.tb_profesor_id,
            'dc_nombre_clase': self.dc_nombre_clase,
            'dc_imagen_url': self.dc_imagen_url
        }