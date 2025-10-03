Se ven bien los espacios entre "bloques" pero los ítems siguen saliendo todos en una misma linea:

Ejemplo

```
📍 Plaza Central de Runegard
Estás en el corazón de la ciudad. El bullicio de mercaderes y aventureros llena el aire. Una imponente fuente de mármol domina el centro de la plaza. Varios caminos parten desde aquí.

🚪 Salidas:
➡️ Este (Calle de los Mercaderes)⬇️ Sur (El Limbo)
```

debeira ser

```
📍 Plaza Central de Runegard
Estás en el corazón de la ciudad. El bullicio de mercaderes y aventureros llena el aire. Una imponente fuente de mármol domina el centro de la plaza. Varios caminos parten desde aquí.

🚪 Salidas:
➡️ Este (Calle de los Mercaderes)
⬇️ Sur (El Limbo)
```

Otro ejemplo

```
📍 El Limbo
Te encuentras en una habitación vacía, suspendida en la nada. Es el comienzo de tu aventura y un refugio seguro.

👁️ Cosas a la vista:- 🎒 una mochila de cuero- 🎒 una mochila de cuero

🚪 Salidas:
⬆️ Norte (Plaza Central de Runegard)
```

debería ser:

```
📍 El Limbo
Te encuentras en una habitación vacía, suspendida en la nada. Es el comienzo de tu aventura y un refugio seguro.

👁️ Cosas a la vista:
- 🎒 una mochila de cuero
- 🎒 una mochila de cuero

🚪 Salidas:
⬆️ Norte (Plaza Central de Runegard)
```

En el inventario pasa lo mismo, el output es:

```
🎒 Tu Inventario
- 🎒 una mochila de cuero- 🎒 una mochila de cuero
```

debería ser:

```
🎒 Tu Inventario
- 🎒 una mochila de cuero
- 🎒 una mochila de cuero
```

