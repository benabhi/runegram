Ya es la tercera vez que pido lo mismo, los items y salidas aparecen en una misma linea, el inventario tabien tiene el mismo error, por ejemplo "- 🎒 una mochila de cuero- 🎒 una mochila de cuero" cada uan de esas deberia estar en su linea.

```
📍 El Limbo
Te encuentras en una habitación vacía, suspendida en la nada. Es el comienzo de tu aventura y un refugio seguro.

👁️ Cosas a la vista:
- 🎒 una mochila de cuero- 🎒 una mochila de cuero

🚪 Salidas:
⬆️ Norte (Plaza Central de Runegard)
```

Deberia quedar asi

```
📍 El Limbo
Te encuentras en una habitación vacía, suspendida en la nada. Es el comienzo de tu aventura y un refugio seguro.

👁️ Cosas a la vista:
- 🎒 una mochila de cuero
- 🎒 una mochila de cuero

🚪 Salidas:
⬆️ Norte (Plaza Central de Runegard)
```

Hacer una analisis de lo que esta pasando para encontrar una solucion definitiva, los bloques, personajes, items y salidas estan bien separadas un un salto de linea en blancom pero es el bucle que genera los items que no los meustra bien.