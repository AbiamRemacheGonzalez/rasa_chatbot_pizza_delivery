from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormAction

import psycopg2
import datetime as dt
import sqlite3

class ActionResetSlots(Action):

    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]

##------------------------------------------------VALIDACIÓN DEL FORMULARIO DEL NOMBRE----------------------------------------------------##
class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"
    
    def validate_nombre(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict)-> Dict[Text, Any]:
        nombre_completo = slot_value.split()
        tamaño = len(nombre_completo)
        if (tamaño == 2):
            return {"nombre" : nombre_completo[0],"primer_apellido" : nombre_completo[1]}
        if (tamaño >= 3):
            db = DataBase()
            db.init_database()
            primer_apellido = nombre_completo[tamaño-2].upper()
            segundo_apellido = nombre_completo[tamaño-1].upper()
            nombre = nombre_completo[0].upper()
            uid = db.cargar_id_de_usuario(nombre, primer_apellido, segundo_apellido)
            dir = db.cargar_direccion_de_usuario(uid)
            db.close_connection()
            if uid != None:
                print("usuario existente")
                return {"nombre" : nombre,"primer_apellido" : primer_apellido, "segundo_apellido": segundo_apellido,"tipo_de_via" : dir[5],"nombre_de_via" : dir[0], "numero_de_via" : dir[1], "numero_de_piso" : dir[2], "puerta": dir[3]}
            else:
                print("usuario no existente")
                return {"nombre" : nombre,"primer_apellido" : primer_apellido, "segundo_apellido": segundo_apellido}
        #tamaño == 1
        return {"nombre" : nombre_completo[0]}

    def validate_primer_apellido(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict)-> Dict[Text, Any]:
        nombre_completo = slot_value.split()
        tamaño = len(nombre_completo)
        if (tamaño == 2):
            db = DataBase()
            db.init_database()
            primer_apellido = nombre_completo[0].upper()
            segundo_apellido = nombre_completo[1].upper()
            nombre = tracker.get_slot("nombre").upper()
            uid = db.cargar_id_de_usuario(nombre, primer_apellido, segundo_apellido)
            dir = db.cargar_direccion_de_usuario(uid)
            db.close_connection()
            if uid != None:
                print("usuario existente")
                return {"primer_apellido" : primer_apellido, "segundo_apellido": segundo_apellido,"tipo_de_via" : dir[5],"nombre_de_via" : dir[0], "numero_de_via" : dir[1], "numero_de_piso" : dir[2], "puerta": dir[3]}
            else:
                print("usuario no existente")
                return {"primer_apellido" : primer_apellido, "segundo_apellido": segundo_apellido}
            return {"primer_apellido" : nombre_completo[0],"segundo_apellido" : nombre_completo[1]}
        return {"primer_apellido" : nombre_completo[0]}
    
    def validate_segundo_apellido(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        nombre_completo = slot_value.split()
        db = DataBase()
        db.init_database()
        primer_apellido = tracker.get_slot("primer_apellido").upper()
        segundo_apellido = nombre_completo[0].upper()
        nombre = tracker.get_slot("nombre").upper()
        uid = db.cargar_id_de_usuario(nombre, primer_apellido, segundo_apellido)
        dir = db.cargar_direccion_de_usuario(uid)
        db.close_connection()
        if uid != None:
            print("usuario existente")
            return {"segundo_apellido": segundo_apellido,"tipo_de_via" : dir[5],"nombre_de_via" : dir[0], "numero_de_via" : dir[1], "numero_de_piso" : dir[2], "puerta": dir[3]}
        else:
            print("usuario no existente")
            return {"segundo_apellido": segundo_apellido}
        



##--------------------------------ACCIÓN DEL FORMULARIO DEL NOMBRE-------------------------------------##
class ActionNameForm(FormAction):
    def name(selft) -> Text:
        return "action_name_form"
    
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["nombre", "primer_apellido", "segundo_apellido"]

    def submit(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict,) -> Dict[Text,Any]:
        n = tracker.get_slot("nombre").upper()
        a1 = tracker.get_slot("primer_apellido").upper()
        a2 = tracker.get_slot("segundo_apellido").upper()
        #dispatcher.utter_message(text=f"Registrado el usuario {n} {a1} {a2}")
        db = DataBase()
        db.init_database()
        id = db.cargar_id_de_usuario(n, a1, a2)
        if id != None:
            dispatcher.utter_message(text=f"El usuario {n} {a1} {a2} ya consta como usuario registrado. ¡Bienvenido!")
        else:
            print("El usuario no existe")
            db.guardar_nombre(n, a1, a2)   
        db.close_connection()
        return []

##------------------------------------VALIDACIÓN DEL FORMULARIO DE LA DIRECCIÓN-------------------------------------##
class ValidateDirForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_dir_form"
    
    def validate_tipo_de_via(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        #Formato: Tipo de via | nombre de via | numero de via
        valores = slot_value.split()
        if len(valores) == 1:
            tipo_de_via = tracker.get_slot("tipo_de_via")
            nombre_de_via = tracker.get_slot("nombre_de_via")
            numero_de_via = tracker.get_slot("numero_de_via")
            return {"tipo_de_via" : tipo_de_via,"nombre_de_via" : nombre_de_via, "numero_de_via" : numero_de_via}
        if next(tracker.get_latest_entity_values("barrio"), None) != None:
            tipo_de_via = next(tracker.get_latest_entity_values("barrio"), None)
        if next(tracker.get_latest_entity_values("calle"), None) != None:
            tipo_de_via = next(tracker.get_latest_entity_values("calle"), None)
        if next(tracker.get_latest_entity_values("alameda"), None) != None:
            tipo_de_via = next(tracker.get_latest_entity_values("alameda"), None)
        if next(tracker.get_latest_entity_values("avenida"), None) != None:
            tipo_de_via = next(tracker.get_latest_entity_values("avenida"), None)
        if next(tracker.get_latest_entity_values("bloque"), None) != None:
            tipo_de_via = next(tracker.get_latest_entity_values("bloque"), None)
        if next(tracker.get_latest_entity_values("acera"), None) != None:
            tipo_de_via = next(tracker.get_latest_entity_values("acera"), None)
        nombre_de_via = slot_value[len(valores[0])+1:]
        numero_de_via = valores[len(valores)-1]
        if numero_de_via.isdigit():
            nombre_de_via = slot_value[len(valores[0])+1:len(slot_value)-len(numero_de_via)-1]
            return {"tipo_de_via" : tipo_de_via,"nombre_de_via" : nombre_de_via, "numero_de_via" : numero_de_via}
        return {"tipo_de_via" : tipo_de_via,"nombre_de_via" : nombre_de_via}

    def validate_nombre_de_via(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        valores = slot_value.split()
        numero_de_via = valores[len(valores)-1]
        if numero_de_via.isdigit():
            nombre_de_via = slot_value[0:len(slot_value)-len(numero_de_via)-1]
            return {"nombre_de_via" : nombre_de_via, "numero_de_via" : numero_de_via}
        return {"nombre_de_via" : slot_value}

    def validate_numero_de_via(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        lista = slot_value.split()
        return {"numero_de_via" : lista[0]}

    def validate_numero_de_piso(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        # Formato = numero de piso | puerta
        lista = slot_value.split()
        numero_de_piso = lista[0]
        if len(lista) > 1:
            puerta = slot_value[len(lista[0])+1:]
            return {"numero_de_piso" : numero_de_piso, "puerta": puerta}
        return {"numero_de_piso" : numero_de_piso}

    def validate_puerta(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict,)-> Dict[Text, Any]:
        lista = slot_value.split()
        return {"puerta" : lista[0]}

##--------------------------------ACCIÓN DEL FORMULARIO DE LA DIRECCIÓN-------------------------------------##
class ActionDirForm(FormAction):
    def name(selft) -> Text:
        return "action_dir_form"
    
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["tipo_de_via", "nombre_de_via", "numero_de_via", "numero_de_piso", "puerta"]

    def submit(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict,) -> List[Dict]:
        #Recuperar los datos extraidos
        n = tracker.get_slot("nombre").upper()
        a1 = tracker.get_slot("primer_apellido").upper()
        a2 = tracker.get_slot("segundo_apellido").upper()
        tv = tracker.get_slot("tipo_de_via").upper()
        nv = tracker.get_slot("nombre_de_via").upper()
        nuv = tracker.get_slot("numero_de_via").upper()
        nup = tracker.get_slot("numero_de_piso").upper()
        p = tracker.get_slot("puerta").upper()
        #Guardar la dirección
        db = DataBase()
        db.init_database()
        idusuario = db.cargar_id_de_usuario(n, a1, a2)
        dir = db.cargar_direccion_de_usuario(idusuario)
        if dir == None:
            db.guardar_direccion(idusuario,tv,nv,nuv,nup,p)
            dispatcher.utter_message(text=f"Registrado el usuario {n} {a1} {a2} con dirección {tv} {nv} número {nuv}, piso {nup} puerta {p}")
        #Mostrar mensaje de resultado
        
        db.close_connection()
        return []
##------------------------------------VALIDACIÓN DEL FORMULARIO DEL PEDIDO DE PIZZA-------------------------------------##
class ValidatePizzaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_pizza_form"
    
    def validate_tipo_de_pizza(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        #Formato: Tipo de pizza | tamaño de pizza | cantidad de pizza
        tipo_de_pizza = next(tracker.get_latest_entity_values("tipo_de_pizza"), None)
        tamano_de_pizza = next(tracker.get_latest_entity_values("tamano_de_pizza"), None)
        cantidad_de_pizza = next(tracker.get_latest_entity_values("cantidad_de_pizza"), None)
        if tamano_de_pizza is None and cantidad_de_pizza is None:
            return {"tipo_de_pizza": tipo_de_pizza}
        if tamano_de_pizza is None:
            return {"tipo_de_pizza": tipo_de_pizza,"cantidad_de_pizza":cantidad_de_pizza}
        if cantidad_de_pizza is None:
            return {"tipo_de_pizza": tipo_de_pizza,"tamano_de_pizza":tamano_de_pizza}
        return {"tipo_de_pizza": tipo_de_pizza,"tamano_de_pizza": tamano_de_pizza,"cantidad_de_pizza":cantidad_de_pizza}
    def validate_tamano_de_pizza(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        tamano_de_pizza = next(tracker.get_latest_entity_values("tamano_de_pizza"), None)
        cantidad_de_pizza = next(tracker.get_latest_entity_values("cantidad_de_pizza"), None)
        if cantidad_de_pizza is None:
            return {"tamano_de_pizza":tamano_de_pizza}
        return {"tamano_de_pizza":tamano_de_pizza, "cantidad_de_pizza":cantidad_de_pizza}
    def validate_cantidad_de_pizza(self,slot_value: Any,dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict)-> Dict[Text, Any]:
        cantidad_de_pizza = next(tracker.get_latest_entity_values("cantidad_de_pizza"), None)
        return {"cantidad_de_pizza":cantidad_de_pizza}
##------------------------------------ACCIÓN DEL FORMULARIO DEL PEDIDO DE PIZZA-------------------------------------##    
class ActionPizzaForm(FormAction):
    def name(selft) -> Text:
        return "action_pizza_form"
    
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["tipo_de_pizza", "tamano_de_pizza", "cantidad_de_pizza"]

    def submit(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict,) -> List[Dict]:
        n = tracker.get_slot("nombre").upper()
        a1 = tracker.get_slot("primer_apellido").upper()
        a2 = tracker.get_slot("segundo_apellido").upper()
        tp = next(tracker.get_latest_entity_values("tipo_de_pizza"), None)
        tap = next(tracker.get_latest_entity_values("tamano_de_pizza"), None)
        cp = next(tracker.get_latest_entity_values("cantidad_de_pizza"), None)
        db = DataBase()
        db.init_database()
        usuarioid = db.cargar_id_de_usuario(n, a1, a2)
        print(tap)
        print(db.sizeOfInv(tap))
        db.guardar_pedido(tp, cp, db.sizeOfInv(tap), usuarioid)
        db.close_connection()
        dispatcher.utter_message(text=f"Se ha registrado el pedido de {cp} pizzas del tipo {tp} en el tamaño {tap}")
        return []

##---------------------------CLASE PARA VISUALIZAR LOS PEDIDOS---------------------------##
class ActionMostrarPedidos(FormAction):
    def name(selft) -> Text:
        return "action_mostrar_pedidos"
    
    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["nombre", "primer_apellido", "segundo_apellido"]

    def submit(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: DomainDict,) -> List[Dict]:
        n = tracker.get_slot("nombre").upper()
        a1 = tracker.get_slot("primer_apellido").upper()
        a2 = tracker.get_slot("segundo_apellido").upper()
        db = DataBase()
        db.init_database()
        usuarioid = db.cargar_id_de_usuario(n, a1, a2)
        if usuarioid != None:
            pedidos = db.cargar_ultimos_pedidos(usuarioid)
            db.close_connection()
            f1 = "%A, %d de %B de %Y"
            f2 = "Hora %H:%M"
            res = ""
            for pedido in pedidos:
                t = db.sizeOf(str(pedido[2]))
                ft = pedido[3].strftime(f1)
                fd = pedido[3].strftime(f2)
                title = "- Pedido "+ft+"\n"
                description = "\t\t"+fd +"=> "+ str(pedido[1]) + " " + str(pedido[0])+" "+t
                res = res + title + "" + description + "\n\n"
            dispatcher.utter_message(text=f"Estos son tus pedidos:\n {res}")
        else:
            dispatcher.utter_message(text=f"El usuario no tiene pedidos")
        return []
##----------------------------CLASE DE BASE DE DATOS------------------------------------------##
class DataBase:
    def init_database(self):
        self.conn = psycopg2.connect(
            host="demo_rasa_postgres",
            port="5432",
            dbname="postgres",
            user="postgres",
            password="1234",
            options="-c search_path=public")
        self.cur = self.conn.cursor()

    def create_new_connection(self,host, port, user, password, database, options):
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=user,
            password=password,
            options=options)
        self.cur = self.conn.cursor()

    def close_connection(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def guardar_nombre(self,nombre, primer_apellido, segundo_apellido):
        SQL = "INSERT INTO usuarios (nombre, primer_apellido, segundo_apellido) VALUES (%s, %s, %s)"
        self.cur.execute(SQL, (nombre, primer_apellido, segundo_apellido))

    def guardar_direccion(self,usuarioid, tipo_de_via, nombre_de_via, numero_de_via, numero_de_piso, puerta):
        SQL = "INSERT INTO direcciones (tipo_de_via, nombre_de_via, numero_de_via, numero_de_piso, puerta, codigo_postal, usuarioid) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.cur.execute(SQL, (tipo_de_via,nombre_de_via,numero_de_via,numero_de_piso,puerta, '35014',usuarioid))

    def cargar_direccion_de_usuario(self, id):
        SQL = "SELECT * FROM direcciones WHERE usuarioid = %s;"
        self.cur.execute(SQL, (id,))
        fetch = self.cur.fetchall()
        if fetch != []:
            return fetch[0]
        else:
            return None

    def cargar_id_de_usuario(self, nombre, primer_apellido, segundo_apellido):
        SQL = "SELECT usuarios.usuarioid FROM usuarios WHERE nombre = %s and primer_apellido = %s and segundo_apellido = %s;"
        self.cur.execute(SQL, (nombre,primer_apellido, segundo_apellido))
        fetch = self.cur.fetchall()
        if fetch != []:
            return fetch[0][0]
        else:
            return None
    def guardar_pedido(self, tipo_de_pizza, cantidad_de_pizza, tamano_de_pizza, usuarioid):
        SQL = "INSERT INTO pedidos (tipo_de_pizza, cantidad_de_pizza, tamano_de_pizza,fecha_de_pedido,usuarioid) VALUES (%s, %s, %s, %s, %s)"
        self.cur.execute(SQL, (tipo_de_pizza,cantidad_de_pizza,tamano_de_pizza,dt.datetime.now(),usuarioid))
    
    def cargar_ultimos_pedidos(self,usuarioid):
        SQL = "SELECT * FROM pedidos WHERE usuarioid = %s;"
        self.cur.execute(SQL, (usuarioid,))
        fetch = self.cur.fetchall()
        if fetch != []:
            return fetch
        else:
            return None
    def sizeOf(self, pizza_size):
        if pizza_size == "0":
            return "pequeña"
        if pizza_size == "1":
            return "mediana"
        if pizza_size == "2":
            return "grande"
    def sizeOfInv(self, pizza_size):
        if pizza_size == "pequeño":
            return 0
        if pizza_size == "mediano":
            return 1
        if pizza_size == "grande":
            return 2