# Release History
## 0.6.0 (2024-02-06)

- The `>>` and `<<` operators of `DATTask` now accept a function directly.
- `DAGTask` now uses the DAG's warehouse by default.
- `DAGTask` accepts a new parameter `session_parameters`.
- Updated `TaskContext`:
  - `get_predecessor_return_value` now works for both long and short names of a `DAGTask`.
  - Added the methods `get_current_task_short_name` and `get_task_graph_config_property`.
- Added support for pydantic 2.x.
- Added support for Python 3.11.
- Fixed a bug where `DAGOperation.run(dag)` raised an exception if the DAG doesn't have a schedule.
- Fixed a bug where deleting a `DAG` didn't delete all of its sub-tasks.
- Fixed a bug that raised an error when a DAG's `config` is set.

## 0.5.1 (2023-12-07)

- Add urllib3 into dependencies.

## 0.5.0 (2023-12-06)

- Removed the experimental tags on all entities.
- Fixed a bug that raised an exception when listing Databases and Schemas.

## 0.4.0 (2023-12-04)
- Fixed a bug that had an exception when listing some entities that have non-alphanumeric characters in the names.
- Updated dependency on `snowflake-snowpark-python` to `1.5.0`.
- Added support for Python 3.11.
- Removed the Pydantic types from the model class.
- Renamed exception class names in `snowflake.core.exceptions`.

## 0.3.0 (2023-11-17)

Initial pre-release.
