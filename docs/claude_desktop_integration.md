# 🚀 OIPA MCP Server - Integración con Claude Desktop

Esta guía te ayudará a integrar el OIPA MCP Server con Claude Desktop para poder usar comandos de lenguaje natural para gestionar pólizas de seguros.

## 📋 Requisitos Previos

### 1. Claude Desktop Instalado
- Descarga e instala Claude Desktop desde: https://claude.ai/desktop
- Asegúrate de que Claude Desktop esté cerrado antes de continuar

### 2. OIPA MCP Server Funcionando
- Verifica que la conexión a la base de datos OIPA funcione:
```bash
python scripts/test_connection.py
```

## 🔧 Configuración Automática

### Opción 1: Script de Configuración Automática (Recomendado)

```bash
# Ejecuta el script de configuración automática
python scripts/setup_claude_desktop.py
```

Este script:
- ✅ Detecta tu sistema operativo
- ✅ Encuentra la ubicación correcta de configuración de Claude Desktop
- ✅ Lee tu configuración de base de datos desde .env
- ✅ Crea la configuración MCP automáticamente
- ✅ Prueba la conectividad del servidor
- ✅ Te da instrucciones específicas para el siguiente paso

### Opción 2: Configuración Manual

Si prefieres configurar manualmente:

#### Windows
1. Abre el explorador y navega a: `%APPDATA%\\Claude\\`
2. Crea o edita el archivo: `claude_desktop_config.json`

#### macOS
1. Abre Finder y navega a: `~/Library/Application Support/Claude/`
2. Crea o edita el archivo: `claude_desktop_config.json`

#### Linux
1. Navega a: `~/.config/claude/`
2. Crea o edita el archivo: `claude_desktop_config.json`

### Contenido del archivo de configuración:

```json
{
  "mcpServers": {
    "oipa-mcp": {
      "command": "python",
      "args": ["-m", "oipa_mcp.server"],
      "cwd": "C:\\\\Tmp\\\\ML\\\\mcp-oipa\\\\oipa-mcp",
      "env": {
        "OIPA_DB_HOST": "192.168.1.50",
        "OIPA_DB_PORT": "1521",
        "OIPA_DB_SERVICE_NAME": "oipadev",
        "OIPA_DB_USERNAME": "oipa",
        "OIPA_DB_PASSWORD": "tu_password_aqui",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "text"
      }
    }
  }
}
```

**⚠️ IMPORTANTE:** Reemplaza:
- `C:\\\\Tmp\\\\ML\\\\mcp-oipa\\\\oipa-mcp` con la ruta real de tu proyecto
- `tu_password_aqui` con la contraseña real de tu base de datos OIPA

## 🧪 Testing Antes de Integrar

### 1. Test de Conectividad de Base de Datos
```bash
python scripts/test_connection.py
```

### 2. Test de Herramientas MCP
```bash
# Test automático de todas las herramientas
python scripts/test_mcp_tools.py

# Test interactivo (modo manual)
python scripts/test_mcp_tools.py --interactive
```

### 3. Test del Servidor MCP
```bash
# Ejecuta el servidor directamente para verificar que inicia
python -m oipa_mcp.server
```

## 🎯 Usando OIPA MCP en Claude Desktop

### 1. Reinicia Claude Desktop
Después de configurar, cierra y vuelve a abrir Claude Desktop completamente.

### 2. Verifica la Integración
En una nueva conversación, deberías ver que las herramientas OIPA están disponibles.

### 3. Comandos de Ejemplo

#### Búsqueda de Pólizas
```
"Busca pólizas que contengan ATL"
"Find policies with status active" 
"Search for policies of Maria Garcia"
"Muéstrame pólizas canceladas"
```

#### Analytics de Pólizas
```
"¿Cuántas pólizas tenemos por estado?"
"How many policies do we have by status?"
"Show me policy distribution"
"Dame estadísticas de pólizas"
```

#### Detalles de Póliza Específica
```
"Show details for policy ATL20055008"
"Muestra detalles de la póliza ATL20055011"
"Get comprehensive information for policy number [número]"
```

## 🔧 Herramientas Disponibles

### 1. `oipa_search_policies`
**Descripción:** Búsqueda inteligente de pólizas por múltiples criterios

**Parámetros:**
- `search_term`: Término de búsqueda (número de póliza, nombre de cliente, tax ID)
- `status_filter`: Filtro por estado (`active`, `cancelled`, `pending`, `all`)
- `limit`: Número máximo de resultados (default: 50)

**Ejemplo de uso:**
```
"Search for policies with Maria in the name"
"Find active policies"
"Show me the first 10 policies containing ATL"
```

### 2. `oipa_get_policy_details`
**Descripción:** Información completa y detallada de una póliza específica

**Parámetros:**
- `policy_number`: Número de póliza (requerido)
- `policy_guid`: GUID de póliza (alternativo)
- `include_segments`: Incluir información de segmentos (opcional)

**Ejemplo de uso:**
```
"Show complete details for policy ATL20055008"
"Get all information about policy number [número]"
```

### 3. `oipa_policy_counts_by_status`
**Descripción:** Dashboard analítico con distribución de pólizas por estado

**Parámetros:** Ninguno (ejecuta automáticamente)

**Ejemplo de uso:**
```
"How many policies do we have by status?"
"Show me policy distribution"
"Give me a summary of policy counts"
```

## 🐛 Troubleshooting

### Problema: Las herramientas OIPA no aparecen en Claude Desktop

**Soluciones:**
1. **Verifica la configuración:**
   ```bash
   # En Windows
   type "%APPDATA%\\Claude\\claude_desktop_config.json"
   
   # En macOS/Linux  
   cat ~/.config/claude/claude_desktop_config.json
   ```

2. **Verifica que Claude Desktop esté completamente cerrado y reiniciado**

3. **Comprueba los logs de Claude Desktop** (ubicación varía por OS)

4. **Ejecuta test manual:**
   ```bash
   python scripts/test_mcp_tools.py
   ```

### Problema: Error de conexión a base de datos

**Soluciones:**
1. **Verifica conectividad:**
   ```bash
   python scripts/test_connection.py
   ```

2. **Revisa configuración en .env:**
   ```
   OIPA_DB_HOST=192.168.1.50
   OIPA_DB_PORT=1521
   OIPA_DB_SERVICE_NAME=oipadev
   OIPA_DB_USERNAME=oipa
   OIPA_DB_PASSWORD=tu_password_real
   ```

3. **Verifica que el servidor Oracle esté ejecutándose**

4. **Comprueba permisos de red/firewall**

### Problema: Python no encontrado

**Soluciones:**
1. **Verifica instalación de Python:**
   ```bash
   python --version
   ```

2. **Asegúrate de que Python esté en el PATH del sistema**

3. **En la configuración, usa la ruta completa a Python:**
   ```json
   "command": "C:\\\\Python39\\\\python.exe"
   ```

### Problema: Módulos no encontrados

**Soluciones:**
1. **Instala dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verifica el entorno virtual si lo usas**

3. **Comprueba que el `cwd` en la configuración sea correcto**

## 📊 Monitoring y Logs

### Ver logs del servidor MCP:
```bash
# Con nivel DEBUG para más información
LOG_LEVEL=DEBUG python -m oipa_mcp.server
```

### Logs de Claude Desktop:
- Windows: `%APPDATA%\\Claude\\logs\\`
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.local/share/claude/logs/`

## 🚀 Próximos Pasos

Una vez que tengas la integración funcionando:

1. **Experimenta con diferentes consultas** para familiarizarte con las capacidades
2. **Documenta los casos de uso** más útiles para tu organización
3. **Considera extensiones** como herramientas adicionales para clientes o transacciones
4. **Implementa monitoring** en producción si planeas uso extensivo

## 📞 Soporte

Si encuentras problemas:

1. **Ejecuta los scripts de diagnóstico** incluidos
2. **Revisa los logs** del servidor MCP y Claude Desktop
3. **Verifica la configuración** paso a paso
4. **Prueba la conectividad** de base de datos independientemente

¡La integración OIPA MCP + Claude Desktop te permitirá gestionar pólizas de seguros usando lenguaje natural de manera intuitiva y eficiente!
