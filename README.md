# Sistema Integral de Gestión – Software FJ

Proyecto académico para la Fase 4 del curso Programación (213023), UNAD.

## Requisitos
- Python 3.9 o superior.
- No requiere instalar paquetes externos.
- No utiliza bases de datos. La información se mantiene en listas y objetos en memoria.
- El archivo `logs/software_fj.log` se crea automáticamente al ejecutar el programa.

## Ejecución
Desde una terminal, dentro de esta carpeta:

```bash
python main.py
```

## Funcionalidades
- Clase abstracta `Entidad` y clase `Cliente` con atributos encapsulados y validaciones.
- Clase abstracta `Servicio` y tres clases derivadas: `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`.
- Polimorfismo mediante `describir`, `validar_parametros` y `calcular_costo` sobrescritos.
- `Reserva` permite confirmar, cancelar y calcular costos.
- Excepciones personalizadas, `try/except`, `try/except/else`, `try/finally` y encadenamiento con `raise ... from exc`.
- Registro de eventos y errores mediante el módulo `logging`.
- Demostración de más de diez operaciones válidas e inválidas.

## Estructura
```text
SoftwareFJ_Fase4/
├── main.py
├── README.md
├── .gitignore
└── logs/
    └── (software_fj.log se genera al ejecutar)
```

## Nota sobre métodos sobrecargados
Python no implementa sobrecarga tradicional por firma como otros lenguajes. En este proyecto se demuestra una alternativa idiomática mediante parámetros opcionales en `calcular_costo`, 
permitiendo calcular con tarifa base, impuesto y descuento. Las clases especializadas sobrescriben el método para aplicar duración y unidades según el tipo de servicio.

## Evidencias recomendadas para la entrega
1. Captura de la ejecución de `python main.py` donde se vean las operaciones y errores controlados.
2. Captura del archivo `logs/software_fj.log` con eventos y errores.
3. Enlace al repositorio GitHub del equipo y evidencia de ramas/commits de los integrantes.
4. Explicación breve de las clases, la herencia, el polimorfismo y el manejo de excepciones.
