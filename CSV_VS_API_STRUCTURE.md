# CSV vs API: Estructura de Carpetas en Testmo Export

**Fecha**: 2026-01-30
**Problema**: Export con `--csv-map` destruyó la estructura anidada de carpetas

## El Problema

Al exportar con `--csv-map`, se creó una estructura PLANA (126 carpetas de nivel 1, 0 carpetas anidadas), perdiendo completamente la jerarquía organizacional de Testmo.

### Comparación

#### ❌ CON `--csv-map` (INCORRECTO)
```bash
python scripts/testmo_export.py \
  --project-id 2 \
  --csv-map data/oneapp-repo-export.csv \
  --output-dir testmo/oneapp/test-cases
```

**Resultado:**
- 126 carpetas de nivel 1 (todas planas)
- 0 carpetas anidadas
- Estructura: `enhanced-in-app-chat/`, `collision-management/`, `schedule-service/`

**Por qué falló:**
El CSV de Testmo solo tiene una columna "Folder" con el NOMBRE de la carpeta, NO la ruta completa:
```csv
"Case ID","Case","Folder"
"535","Fresh Install","Installation"
"540","Demo Mode","Home"
"64828","Enhanced Chat","Enhanced In-App Chat"
```

No hay información de jerarquía. No sabemos si "Enhanced In-App Chat" está en `support/` o en root.

#### ✅ SIN `--csv-map` (CORRECTO)
```bash
python scripts/testmo_export.py \
  --project-id 2 \
  --output-dir testmo/oneapp/test-cases
```

**Resultado:**
- 99 carpetas totales
- 79 carpetas anidadas (nivel 2+)
- Estructura correcta con hasta 4 niveles de profundidad

**Ejemplos de jerarquía preservada:**
```
vehicle/
├── collision-management-nna-only/ (46 casos)
├── second-delivery/
│   └── second-delivery-booking-virtual/
├── schedule-service/
│   └── create/
└── vehicle-profile/

old-deprecated/
├── ccs2/
│   ├── home/
│   │   └── climate/
│   │       └── hvac-parameters/
│   ├── multi-user-alerts/
│   └── multi-user-destination-send-to-car/
└── schedule-service/

support/
├── let-us-help/
├── parts-and-accessories-nci-nis-and-inf/
└── enhanced-in-app-chat/

settings/
├── marketing-preferences/
├── edit-profile-delete-account-page-using-sso-nna-nis-and-inf-only/
└── ncf/

map/
└── route-planner/
```

## Por qué el API es Superior

| Característica | CSV | API |
|---------------|-----|-----|
| Jerarquía de carpetas | ❌ Solo nombres | ✅ Rutas completas |
| Niveles de profundidad | ❌ 1 nivel (plano) | ✅ Hasta 4+ niveles |
| Organización | ❌ Perdida | ✅ Preservada |
| Carpetas eliminadas | ❌ No detecta | ✅ Detecta y alerta |
| Datos de origen | CSV estático | API en tiempo real |

## Casos con Folder IDs Eliminados

El export API detectó 528 casos con folder_ids que ya no existen en Testmo:
- `folder_id=39, 40, 41, 44, 50-55, 66, 6799-6816, 7144`
- Estos fueron movidos a `uncategorized/` automáticamente
- Necesitan ser re-categorizados manualmente en Testmo UI

## Estadísticas del Export Correcto

```
Total casos: 1334
Carpetas totales: 99
Carpetas anidadas: 79
Archivos en root: 0
Casos sin carpeta válida: 528 (39.6%)
```

**Top folders con estructura anidada:**
```
vehicle/collision-management-nna-only: 46 casos
vehicle/second-delivery: 30 casos
vehicle/vehicle-profile: 28 casos
map/route-planner: 25 casos
vehicle/telematics-bsm-subscriptions-packages: 22 casos
vehicle/proactive-maintenance: 22 casos
support/let-us-help: 19 casos
vehicle/schedule-service/create: 18 casos
old-deprecated/ccs2/multi-user-destination-send-to-car: 18 casos
```

## Cuándo Usar Cada Método

### Usar API (SIN --csv-map) ✅
- **Siempre que sea posible**
- Cuando necesitas preservar la jerarquía organizacional
- Para proyectos con estructura de carpetas anidadas
- Cuando quieres detectar folders eliminados

### Usar CSV (CON --csv-map) ⚠️
- **Solo en casos excepcionales**
- Cuando el API no tiene la estructura de carpetas (folders eliminados)
- Para proyectos completamente planos (1 nivel)
- Cuando el CSV tiene información que el API no tiene

**IMPORTANTE:** Nunca uses `--csv-map` para OneApp, NMEX, NBA, o cualquier proyecto con estructura organizacional compleja.

## Comandos Correctos para Cada Proyecto

### OneApp (1334 casos)
```bash
python scripts/testmo_export.py \
  --project-id 2 \
  --output-dir testmo/oneapp/test-cases
```

### NMEX (284 casos)
```bash
python scripts/testmo_export.py \
  --project-id 3 \
  --output-dir testmo/nmex/test-cases
```

### NBA (50 casos)
```bash
python scripts/testmo_export.py \
  --project-id 4 \
  --output-dir testmo/nba/test-cases
```

### Enrique Playground (8 casos)
```bash
python scripts/testmo_export.py \
  --project-id 8 \
  --output-dir testmo/enrique-playground/test-cases
```

## Lección Aprendida

**El CSV de Testmo NO contiene la jerarquía de carpetas.**
Solo contiene nombres de carpetas individuales, sin información de nesting.

Para preservar la estructura organizacional, **siempre usa el API** (sin `--csv-map`).

## Status

- ✅ Estructura corregida para OneApp
- ✅ 79 carpetas anidadas preservadas
- ✅ 0 archivos en root
- ✅ Jerarquía de hasta 4 niveles funcionando
- ⚠️ 528 casos en "uncategorized" (folders eliminados en Testmo)

**Siguiente paso:** Revisar y re-categorizar los 528 casos en "uncategorized" directamente en Testmo UI.
