from werkzeug.security import check_password_hash
# from flask_login import UserMixin # type: ignore

class User():
    def __init__(self, id, dc_nombre=None, dc_contrasena=None, dc_correo_electronico=None, dc_telefono=None) -> None:
        self.id = id
        self.dc_nombre = dc_nombre
        self.dc_contrasena = dc_contrasena
        self.dc_correo_electronico = dc_correo_electronico
        self.dc_telefono = dc_telefono
        
    @classmethod    
    def check_password(self, hashed_password,password):
        return check_password_hash(hashed_password,password)
    
    def to_JSON(self):
        return {
            'id': self.id,
            'dc_nombre': self.dc_nombre,
            'dc_contrasena': self.dc_contrasena,
            'dc_correo_electronico': self.dc_correo_electronico,
            'dc_telefono': self.dc_telefono
        }