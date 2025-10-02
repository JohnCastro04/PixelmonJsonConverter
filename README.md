# JSON Converter - Django Web Application

Este proyecto es una aplicación web Django que convierte archivos JSON del formato OLD (obsoleto) al formato NEW con las siguientes características:

- **Orden de llaves estricto**: Reorganiza las llaves del JSON en un orden específico predefinido
- **Wrapper de predicados**: Envuelve los modelos con predicados del tipo "pixelmon:always"
- **Tags de paleta**: Asegura que todas las paletas tengan sus tags correspondientes
- **Datos de crecimiento por defecto**: Agrega automáticamente datos de crecimiento al final de cada forma

## Características

### Métodos de Conversión

1. **Archivo Individual**: Convierte un solo archivo JSON
2. **Conversión en Lote (ZIP)**: Procesa múltiples archivos JSON desde un archivo ZIP
3. **Entrada de Texto**: Convierte JSON directamente desde un área de texto

### Funcionalidades Web

- Interfaz intuitiva y moderna
- Drag & drop para archivos
- Log de actividad en tiempo real
- Descarga automática de archivos convertidos
- Validación de JSON en tiempo real
- Diseño responsivo para dispositivos móviles

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Si tienes el proyecto en un repositorio
   git clone <url-del-repositorio>
   cd json_converter_project
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar migraciones de Django**
   ```bash
   python manage.py migrate
   ```

5. **Ejecutar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

6. **Acceder a la aplicación**
   
   Abre tu navegador y ve a: `http://localhost:8000`

## Uso

### 1. Conversión de Archivo Individual

- Haz clic en "Seleccionar archivo JSON"
- Elige tu archivo .json en formato OLD
- Haz clic en "Convertir Archivo"
- El archivo convertido se descargará automáticamente con el sufijo "_new.json"

### 2. Conversión en Lote (ZIP)

- Crea un archivo ZIP con todos los archivos .json que deseas convertir
- Selecciona el archivo ZIP y haz clic en "Convertir ZIP"
- Se descargará un nuevo ZIP con todos los archivos convertidos

### 3. Conversión desde Texto

- Pega tu JSON en formato OLD en el área de texto izquierda
- Haz clic en "Convertir"
- El JSON convertido aparecerá en el área de texto derecha
- Puedes copiar el resultado o descargarlo como archivo

### Atajos de Teclado

- **Ctrl+Enter** (Windows/Linux) o **Cmd+Enter** (macOS): Convertir texto
- **Escape**: Cerrar modal de progreso

### Drag & Drop

Puedes arrastrar archivos directamente sobre las áreas de selección de archivos para una experiencia más fluida.

## Estructura del Proyecto

```
json_converter_project/
├── json_converter_project/     # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── converter/                  # Aplicación principal
│   ├── templates/converter/    # Templates HTML
│   │   ├── base.html
│   │   ├── index.html
│   │   └── help.html
│   ├── static/converter/       # Archivos estáticos
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── conversion_logic.py     # Lógica de conversión portada
│   ├── views.py               # Vistas de Django
│   ├── urls.py               # URLs de la aplicación
│   └── apps.py               # Configuración de la app
├── manage.py                 # Script de gestión de Django
├── requirements.txt          # Dependencias de Python
└── README.md                # Este archivo
```

## Limitaciones

- Los archivos deben estar en formato JSON válido
- Los archivos ZIP no deben exceder 10MB
- Solo se procesan archivos .json dentro de los ZIP
- Los archivos que ya tengan el sufijo "_new.json" serán ignorados en conversiones ZIP

## Ejemplo de Conversión

### Formato OLD (antes):
```json
{
  "name": "Pikachu",
  "forms": [
    {
      "name": "base",
      "genderProperties": [
        {
          "gender": "male",
          "palettes": [
            {
              "name": "none",
              "texture": "pixelmon/textures/pokemon/pikachu.png",
              "modelLocator": {
                "pqc": ["models/pokemon/pikachu.pqc"]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Formato NEW (después):
```json
{
  "name": "Pikachu",
  "dex": 25,
  "defaultForms": ["base"],
  "forms": [
    {
      "name": "base",
      "genderProperties": [
        {
          "gender": "male",
          "palettes": [
            {
              "name": "none",
              "models": [
                {
                  "model_predicate": {
                    "type": "pixelmon:always"
                  },
                  "models": [
                    {
                      "texture": "pixelmon/textures/pokemon/pikachu.png",
                      "model": "models/pokemon/pikachu.bmd",
                      "animations": [
                        {
                          "type": "idle",
                          "animation": "models/pokemon/idle.bmd"
                        },
                        {
                          "type": "walk",
                          "animation": "models/pokemon/walk.bmd"
                        }
                      ],
                      "scale": 1.0
                    }
                  ]
                }
              ],
              "tags": []
            }
          ]
        }
      ],
      "growth_data": {
        "mean": 40.0,
        "standard_deviation": 2.0,
        "min_render_scale": 0.7,
        "max_render_scale": 1.3
      }
    }
  ]
}
```

## Desarrollo

### Agregar Nuevas Funcionalidades

1. Modifica `converter/conversion_logic.py` para cambios en la lógica de conversión
2. Actualiza `converter/views.py` para nuevas vistas o endpoints
3. Modifica los templates en `converter/templates/converter/` para cambios en la UI
4. Actualiza los estilos CSS en `converter/static/converter/css/style.css`

### Ejecutar en Producción

Para deployar en producción:

1. Configura `DEBUG = False` en `settings.py`
2. Configura `ALLOWED_HOSTS` con tus dominios
3. Usa un servidor web como Nginx + Gunicorn
4. Configura variables de entorno para settings sensibles

## Licencia

Este proyecto está basado en la aplicación GUI original de conversión JSON y ha sido adaptado para funcionar como una aplicación web Django.

## Contribuciones

Si encuentras errores o tienes sugerencias de mejoras, por favor revisa el log de actividad en la aplicación para obtener información detallada sobre cualquier problema.