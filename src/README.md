# Estructura del Proyecto

Este proyecto sigue una estructura organizada y escalable para facilitar el mantenimiento y desarrollo.

## Estructura de Carpetas

```
src/
├── components/          # Componentes reutilizables
│   ├── DocumentButton.js
│   └── DocumentList.js
│
├── pages/              # Páginas/Vistas principales
│   ├── LoginScreen.js
│   └── InspectionScreen.js
│
├── styles/             # Archivos CSS
│   ├── InspectionScreen.css
│   └── LoginScreen.css
│
├── constants/          # Constantes y datos iniciales
│   └── documents.js
│
├── utils/              # Funciones utilitarias (para implementar)
│
├── App.js              # Componente principal
├── App.css
├── index.js            # Punto de entrada
└── index.css
```

## Descripción de Carpetas

### `/components`
Componentes reutilizables que pueden ser usados en múltiples páginas:
- **DocumentButton.js**: Botón individual para cada documento
- **DocumentList.js**: Lista de botones de documentos

### `/pages`
Vistas completas de la aplicación:
- **LoginScreen.js**: Pantalla de inicio de sesión
- **InspectionScreen.js**: Pantalla principal de inspección

### `/styles`
Archivos CSS organizados por componente o página

### `/constants`
Datos constantes y configuraciones:
- **documents.js**: Lista inicial de documentos requeridos

### `/utils`
Funciones auxiliares y helpers (para implementar según necesidad)

## Convenciones de Código

1. **Componentes**: Usar PascalCase para nombres de archivos y componentes
2. **Funciones**: Usar camelCase para nombres de funciones
3. **Constantes**: Usar UPPER_SNAKE_CASE para constantes exportadas
4. **Imports**: Ordenar imports (React, librerías, componentes locales, estilos)

## Próximos Pasos

- Implementar modal para subida de documentos
- Conectar con backend API
- Agregar validación de formularios
- Implementar manejo de errores
