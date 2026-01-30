# Audit de Paginación: API Client

**Fecha**: 2026-01-30
**Objetivo**: Auditar TODOS los métodos del API client que devuelven listas

## Resumen

**Encontrados**: 3 métodos con problemas de paginación
**Status**:
- ✅ 1 FIXED: `list_folders()`
- ❌ 2 BROKEN: `search_cases()`, `list_cases()`

## Métodos Auditados

### 1. ❌ `list_cases()` - PROBLEMA
```python
def list_cases(self, project_id: int, folder_id: Optional[int] = None, limit: int = 100):
    params = {"limit": limit}
    response = self._request("GET", f"/projects/{project_id}/cases", params=params)
    return response.get("result", [])  # ❌ Solo primera página
```

**Problema**:
- Acepta parámetro `limit` pero NO pagina
- Si hay 1000 casos y `limit=100`, solo devuelve 100
- Engañoso: parece que controla cuántos devolver, pero en realidad es un hard limit

**Impacto**: ALTO
- Usado en código que espera todos los casos
- Silenciosamente trunca resultados

**Fix**:
```python
def list_cases(self, project_id: int, folder_id: Optional[int] = None, limit: Optional[int] = None):
    """List test cases with optional limit (no pagination)"""
    all_cases = []
    page = 1
    collected = 0

    while True:
        response = self._request("GET", f"/projects/{project_id}/cases?page={page}")
        cases = response.get("result", [])

        if not cases:
            break

        # Apply limit if specified
        if limit:
            remaining = limit - collected
            cases = cases[:remaining]
            all_cases.extend(cases)
            collected += len(cases)
            if collected >= limit:
                break
        else:
            all_cases.extend(cases)

        if not response.get("next_page"):
            break
        page = response.get("next_page")

    return all_cases
```

**O MEJOR**: Deprecar y usar `get_all_cases()` siempre

### 2. ✅ `get_all_cases()` - OK
```python
def get_all_cases(self, project_id: int, folder_id: Optional[int] = None, debug: bool = False):
    all_cases = []
    page = 1
    while True:
        response = self._request("GET", f"/projects/{project_id}/cases", params={"page": page})
        cases = response.get("result", [])
        if not cases:
            break
        all_cases.extend(cases)
        if not response.get("next_page"):
            break
        page = response.get("next_page")
    return all_cases
```

**Status**: ✅ Correcto
- Maneja paginación correctamente
- Usa `next_page` para continuar
- Loop hasta que no hay más resultados

### 3. ❌ `search_cases()` - PROBLEMA
```python
def search_cases(self, project_id: int, query: Optional[str] = None, ...):
    params = {...}
    response = self._request("GET", f"/projects/{project_id}/cases/search", params=params)
    return response.get("result", [])  # ❌ Solo primera página
```

**Problema**:
- NO maneja paginación
- Si búsqueda devuelve 500 resultados, solo muestra 100
- Silenciosamente pierde 400 resultados

**Impacto**: MEDIO-ALTO
- Búsquedas amplias pierden resultados
- No obvio que faltan resultados

**Fix**:
```python
def search_cases(
    self,
    project_id: int,
    query: Optional[str] = None,
    folder_id: Optional[int] = None,
    tags: Optional[List[str]] = None,
    state_id: Optional[int] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Search test cases with pagination"""
    all_results = []
    page = 1
    collected = 0

    params = {}
    if query:
        params["query"] = query
    if folder_id:
        params["folder_id"] = folder_id
    if tags:
        params["tags"] = ",".join(tags)
    if state_id:
        params["state_id"] = state_id

    while True:
        params["page"] = page
        response = self._request("GET", f"/projects/{project_id}/cases/search", params=params)
        results = response.get("result", [])

        if not results:
            break

        # Apply limit if specified
        if limit:
            remaining = limit - collected
            results = results[:remaining]
            all_results.extend(results)
            collected += len(results)
            if collected >= limit:
                break
        else:
            all_results.extend(results)

        if not response.get("next_page"):
            break
        page = response.get("next_page")

    return all_results
```

### 4. ✅ `list_folders()` - FIXED
```python
def list_folders(self, project_id: int) -> List[Dict[str, Any]]:
    """List all folders in a project with pagination"""
    all_folders = []
    page = 1

    while True:
        response = self._request("GET", f"/projects/{project_id}/folders?page={page}")
        folders = response.get("result", [])
        all_folders.extend(folders)

        next_page = response.get("next_page")
        if not next_page:
            break
        page = next_page

    return all_folders
```

**Status**: ✅ FIXED (2026-01-30)
- Ahora maneja paginación correctamente
- Devuelve 162 folders en lugar de 100
- Resolvió el bug de 528 casos mal clasificados

### 5. ✅ `list_projects()` - OK (No pagination needed)
```python
def list_projects(self) -> List[Dict[str, Any]]:
    response = self._request("GET", "/projects")
    return response.get("result", [])
```

**Status**: ✅ OK
- Típicamente pocos proyectos (< 10)
- No requiere paginación en la práctica

## Recomendaciones

### Inmediato (Esta Semana)
1. ❌ **FIX `search_cases()`** - Agregar paginación
2. ❌ **FIX `list_cases()`** - Agregar paginación O deprecar
3. ✅ **ADD tests** - Test paginación con mock data

### Corto Plazo
1. **Migrar a MCP** - MCP maneja paginación automáticamente
2. **Deprecar métodos** - Marcar `list_cases()` como deprecated, recomendar `get_all_cases()`
3. **Add warnings** - Si método sin paginación devuelve exactamente 100 resultados, advertir

### Patrón Recomendado

Para TODOS los métodos que devuelven listas del API:

```python
def fetch_items(self, endpoint: str, params: dict = None, limit: Optional[int] = None):
    """Generic paginated fetch"""
    all_items = []
    page = 1
    collected = 0

    while True:
        page_params = {**(params or {}), "page": page}
        response = self._request("GET", endpoint, params=page_params)
        items = response.get("result", [])

        if not items:
            break

        # Apply limit if specified
        if limit:
            remaining = limit - collected
            items = items[:remaining]
            all_items.extend(items)
            collected += len(items)
            if collected >= limit:
                break
        else:
            all_items.extend(items)

        # Check for next page
        next_page = response.get("next_page")
        if not next_page:
            break
        page = next_page

    return all_items
```

Luego todos los métodos usan este helper:
```python
def list_cases(self, project_id: int, folder_id: Optional[int] = None):
    params = {"folder_id": folder_id} if folder_id else {}
    return self.fetch_items(f"/projects/{project_id}/cases", params)

def search_cases(self, project_id: int, query: str = None, ...):
    params = {"query": query, ...}
    return self.fetch_items(f"/projects/{project_id}/cases/search", params)

def list_folders(self, project_id: int):
    return self.fetch_items(f"/projects/{project_id}/folders")
```

## Impacto del Bug

### `list_folders()` (FIXED)
- **Casos afectados**: 528 de 1334 (39.6%)
- **Folders perdidos**: 62 de 162 (38.3%)
- **Severidad**: 🔴 CRÍTICO

### `search_cases()` (PENDIENTE)
- **Casos afectados**: Depende de búsqueda
- **Severidad**: 🟡 MEDIO
- **Escenario**: Búsqueda de "Home" devuelve 300 resultados, solo muestra 100

### `list_cases()` (PENDIENTE)
- **Casos afectados**: Todos si se usa sin `get_all_cases()`
- **Severidad**: 🟠 MEDIO-ALTO
- **Escenario**: Folder con 150 casos, solo muestra 100

## Testing

### Test Cases Necesarios
```python
def test_pagination_list_folders():
    """Test that list_folders() returns ALL folders"""
    client = TestmoClient()
    folders = client.list_folders(project_id=2)
    assert len(folders) == 162  # Not 100

def test_pagination_search_cases():
    """Test that search_cases() returns ALL results"""
    client = TestmoClient()
    results = client.search_cases(project_id=2, query="Home")
    # If there are 300 results, should return 300, not 100
    assert len(results) > 100 or response.get("total") <= 100

def test_pagination_list_cases():
    """Test that list_cases() handles pagination"""
    client = TestmoClient()
    cases = client.list_cases(project_id=2)
    # Should return all cases in project
    all_cases = client.get_all_cases(project_id=2)
    assert len(cases) == len(all_cases)
```

## Conclusión

**Bugs encontrados**: 3 métodos sin paginación correcta
- ✅ 1 FIXED: `list_folders()`
- ❌ 2 PENDIENTES: `search_cases()`, `list_cases()`

**Acción inmediata requerida**:
1. Fix `search_cases()` y `list_cases()`
2. Agregar tests de paginación
3. Migrar a MCP (maneja paginación automáticamente)

**Lección**: **SIEMPRE** implementar paginación en métodos que devuelven listas del API.
