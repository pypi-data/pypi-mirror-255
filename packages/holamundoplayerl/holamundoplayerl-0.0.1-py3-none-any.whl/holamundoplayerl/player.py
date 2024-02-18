"""
este es el modulo que incluye la clase del reproductor de musica
"""


class Player:
    """
    Esta clase crea un reproductor
    de musica 
    """

    def play(self, song):
        """
        Reproduce la cancion que recibio como 
        parametro

        Parameters:
        song (str): este es un string con el path
        de la cancion 

        Returns:
        int: devuelve 1 si reproduce con exito, en caso contrario devuelve 0
        """
        print("reproduciendo cancion")

    def stop(self):
        print("stopping")
