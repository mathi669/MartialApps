from werkzeug.security import check_password_hash
from app.utils.DateFormat import DateFormat
# from flask_login import UserMixin # type: ignore

class User():
    def __init__(
            self,
            dc_nombre=None, 
            dc_contrasena=None, 
            dc_correo_electronico=None, 
            dc_telefono=None,
            tb_nivel_artes_marciales_id = None,
            df_fecha_solicitud=None,
            tb_tipo_usuario_id=None,
            tb_usuario_estado_id=None,
            tb_nivel_id=None,
            tb_contacto_emergencia_id=None,
            ) -> None:
        self.dc_nombre = dc_nombre
        self.dc_contrasena = dc_contrasena
        self.dc_correo_electronico = dc_correo_electronico
        self.dc_telefono = dc_telefono
        self.tb_nivel_artes_marciales_id = tb_nivel_artes_marciales_id
        self.df_fecha_solicitud = df_fecha_solicitud 
        self.tb_tipo_usuario_id = tb_tipo_usuario_id
        self.tb_usuario_estado_id = tb_usuario_estado_id
        self.tb_nivel_id = tb_nivel_id
        self.tb_contacto_emergencia_id = tb_contacto_emergencia_id
        
    @classmethod    
    def check_password(self, hashed_password,password):
        return check_password_hash(hashed_password,password)
    
    def to_JSON(self):
        formatted_date = None
        if self.df_fecha_solicitud is not None:
            formatted_date = DateFormat.convert_date(self.df_fecha_solicitud)
        return {
            'dc_nombre': self.dc_nombre,
            'dc_contrasena': self.dc_contrasena,
            'dc_correo_electronico': self.dc_correo_electronico,
            'dc_telefono': self.dc_telefono,
            'tb_nivel_artes_marciales_id': self.tb_nivel_artes_marciales_id,
            'df_fecha_solicitud': formatted_date,
            'tb_tipo_usuario_id': self.tb_tipo_usuario_id,
            'tb_usuario_estado_id': self.tb_usuario_estado_id,
            'tb_nivel_id': self.tb_nivel_id,
            'tb_contacto_emergencia_id': self.tb_contacto_emergencia_id
        }