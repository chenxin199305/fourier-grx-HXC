# fourier-grx 架构缺陷记录

> 分析时间：2026-03-24  
> 状态：已记录，待规划优化方案  
> 范围：`src/fourier_grx/` + `fourier-core/`（submodule）

---

## 背景

fourier-grx 当前架构以"单进程、单机器人、全局共享"为隐含假设设计。这在单人开发时够用，但在多人并行开发时，配置、Task 注册、测试环境三个维度都缺乏隔离机制，导致协作摩擦严重。

---

## 问题清单

### P0 — 严重（直接导致合并冲突或测试无法隔离）

---

#### ISSUE-01：Task `__init__.py` 手动维护导入，频繁引发合并冲突

**位置：**
- `src/fourier_grx/task/grmini1/__init__.py`（267 行手写导入，对应 81 个 Task 文件）
- `src/fourier_grx/task/grmini3/__init__.py`、`n1/`、`m4l/`、`hxc/` 等（结构相同）

**现象：**
每次新增一个 Task，开发者必须手动在 `__init__.py` 末尾添加一行导入：
```python
from fourier_grx.task.grmini1.fi_task_grmini1_new_task import TaskGRMini1NewTask
```
两名开发者同时给同一机器人增加任务时，必然在同一文件同一区域产生 Git 合并冲突。

**影响范围：** 所有机器人型号的 task 子目录，合并冲突是日常高频问题。

---

#### ISSUE-02：全局单例泛滥，测试和并行开发无法隔离

**位置：**

| 单例类 | 文件 |
|--------|------|
| `ControlSystem` | `src/fourier_grx/control_system/fi_control_system.py:18-22` |
| `RobotFactory` | `src/fourier_grx/robot/fi_robot_factory.py:17-24` |
| `CallbackSystemExit` | `src/fourier_grx/callback/fi_callback.py:8-12` |
| `DynalinkManager` 及其子类 | `src/fourier_grx/comm/fi_dynalink_*.py`（9 个文件）|
| `SyncServerZenoh`、`DDS_Server` 等 | `src/fourier_grx/process/sync/`（6 个文件）|
| 各类虚拟外设 | `src/fourier_grx/peripheral/fi_peripheral_virtual_*.py`（5 个文件）|

**典型代码：**
```python
# 任何地方都可以直接获取全局实例，没有依赖注入
ControlSystem().debug_mode(...)
ControlSystem().robot_control_loop_run()
RobotFactory()  # 返回唯一机器人实例
```

**影响范围：** 25+ 个调用点。同一进程只能存在一个机器人实例，两个开发者的测试用例会互相覆盖全局状态。

---

#### ISSUE-03：`gl_config` 全局配置被 32 个文件直接引用，运行时不可切换

**位置：**
- 定义：`fourier-core/src/fourier_core/config/fi_config.py`（submodule）
- 直接引用：32 个文件，包括 `robot/`、`process/`、`config/`、`main/main.py` 等

**现象：**
`gl_config` 在模块加载时就固化了机器人型号、资源路径等配置，并在模块顶层派生出次级全局对象：
```python
# src/fourier_grx/config/resource.py（模块级，加载即固化）
gl_resource = Resource()

# src/fourier_grx/config/record.py（模块级，加载即固化）
gl_record = Record()
```

**影响范围：** 无法在不重启进程的情况下切换配置；不同开发者无法并行测试不同的配置组合。

---

### P1 — 高（架构腐化、重构风险高）

---

#### ISSUE-04：Task ↔ Robot 循环依赖

**位置：**
```
src/fourier_grx/robot/grmini1/fi_robot_grmini1.py
    └─ from fourier_grx.task.grmini1 import *   ← Robot 导入所有 Task

src/fourier_grx/task/grmini1/fi_task_grmini1_idle.py
    └─ from fourier_grx.algorithm.grmini1 import ...
    └─ from fourier_grx.task.fi_task_registry import TaskRegistry
    └─ from fourier_grx.fsm import *
```

Robot 导入所有 Task，Task 反过来引用 Robot、Algorithm、FSM。

**影响范围：** 重构任何一层都必须同时理解并修改其他几层；不同机器人团队的代码高度耦合，改动极易引发连锁错误。

---

#### ISSUE-05：257 处 `from fourier_grx.predefine import *` 导致命名空间污染

**位置：**
- `src/fourier_grx/predefine/__init__.py`（聚合导入 18 个枚举文件）
- 被 wildcard import 的文件：257 个

**现象：**
```python
# 几乎所有模块顶部都有：
from fourier_grx.predefine import *
```
新增或修改任何枚举值，影响范围覆盖全仓库，没有工具能精确告知真实影响面。

**影响范围：** 257 个文件，枚举变更的影响评估成本极高。

---

### P2 — 中（开发效率和维护成本问题）

---

#### ISSUE-06：跨机器人代码严重重复，基类同步困难

**位置：**

每款机器人（grmini1/grmini3/n1/m4l/hxc）在以下目录各有一套平行结构：
- `src/fourier_grx/robot/{model}/`
- `src/fourier_grx/task/{model}/`（grmini1 单独 81 文件，8487 行）
- `src/fourier_grx/algorithm/{model}/`
- `src/fourier_grx/end_effector/{model}/`

**重复示例：**
```python
# task/menu/fi_task_menu_grmini1.py
TASK_STAND_CONTROL = 3010

# task/menu/fi_task_menu_grmini3.py
TASK_STAND_CONTROL = 3010  ← 重复定义，无共享机制
```

**影响范围：** 基类改动必须手动同步到 6+ 个机器人实现；新增机器人型号需复制整套结构，认知成本极高。

---

## 数据汇总

| 指标 | 数值 |
|------|------|
| 使用单例模式的类 | 34 个 |
| 直接引用 `gl_config` 的文件 | 32 个 |
| 使用 `from predefine import *` 的文件 | 257 个 |
| grmini1 task 文件数 | 81 个 |
| grmini1 task 代码总行数 | 8,487 行 |
| 单个最大文件行数（fi_inputs.py） | 3,753 行 |
| 受 ISSUE-01 影响的机器人型号 | 6 个（grmini1/grmini3/gr3mini/n1/m4l/hxc）|

---

## 待办

优化方案和执行计划待后续制定。
