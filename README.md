
# Como se conecta la APP a la BD en desarrollo

Primero se establece un tunel ssh para conexión
```
ssh -L 5433:localhost:5432 enlopez@gate.dcc.uchile.cl -p 202 -N
```

Crear archivo .env con datos de la db del servidor