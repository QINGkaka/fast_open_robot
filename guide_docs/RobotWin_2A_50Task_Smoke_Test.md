# RoboTwin Experiment 2A：50 任务 Action Mode Smoke Test

## 1. 目的

本次 smoke test 用于筛选适合 Experiment 2A 的 RoboTwin 任务。目标是初步判断：

1. 同一任务的原始轨迹中是否存在可区分的动作轨迹簇；
2. 初始画面近似相似时，是否能观察到明显不同的动作轨迹；
3. 哪些任务值得进一步使用 simulator 的真实初始物体位姿进行验证。

本次结果只用于候选任务筛选，不能替代正式的 2A 实验。

## 2. 数据

数据目录：

```text
/share/project/liyuanyuan/data/RoboTwin2.0_clean/RoboTwin_lerobot_v21
```

数据集当前包含：

- 50 个 RoboTwin 任务；
- 每个任务 50 条 episode；
- 总计 2500 条 episode；
- 每个任务对应一个连续的 50-episode block；
- 当前视频和 parquet 数据均成功读取。

因此，当前 clean LeRobot 数据是每任务 50 条，而不是每任务 100 条。

Seen/OOD 划分使用：

[`data/robotwin_ood_clean/splits.json`](../data/robotwin_ood_clean/splits.json)

## 3. Smoke Test 方法

### 3.1 初始场景特征

从每条 episode 的高位相机视频中读取第一帧，使用 PyAV 软件解码 AV1 视频。首帧经过裁剪、缩放，并提取：

- RGB 图像像素特征；
- 灰度图横向和纵向变化特征。

该特征只用于近似判断初始画面相似性。数据文件中没有直接保存 simulator 的物体初始位姿，因此首帧不能等价于真实 simulator state。

### 3.2 动作轨迹特征

每条 episode 提取：

- 14 维动作相对于初始动作的轨迹；
- 32 个归一化时间采样点；
- 左右臂关节运动量；
- 左右臂激活比例；
- 轨迹持续时间。

动作特征经过标准化后使用 KMeans 聚类，分别测试 `K=2/3/4`，选择 silhouette score 最高的结果。

### 3.3 指标定义

- `K`：选择的聚类数。
- `Silhouette`：动作轨迹聚类的 silhouette score，越高表示动作簇越清晰。
- `簇大小`：各动作簇中的轨迹数量。
- `NN`：对每条轨迹寻找首帧图像最近邻，统计最近邻和自身属于不同动作簇的数量。
- `CloseFar`：首帧视觉距离处于本任务最近 20%，动作距离处于最远 20%，且动作簇不同的轨迹 pair 数量。

`CloseFar` 是每个任务内部的相对指标，不同任务之间不能直接视为绝对可比的样本数量。

## 4. 40 个 Seen 任务结果

| 任务 | K | Silhouette | 簇大小 | NN | CloseFar |
|---|---:|---:|---|---:|---:|
| `open_laptop` | 2 | 0.619 | 25/25 | 7 | 52 |
| `place_burger_fries` | 2 | 0.174 | 31/19 | 14 | 29 |
| `place_object_basket` | 3 | 0.664 | 1/29/20 | 1 | 0 |
| `rotate_qrcode` | 2 | 0.675 | 31/19 | 0 | 23 |
| `stamp_seal` | 2 | 0.672 | 20/30 | 1 | 9 |
| `beat_block_hammer` | 2 | 0.870 | 23/27 | 0 | 19 |
| `handover_mic` | 2 | 0.663 | 27/23 | 0 | 6 |
| `place_can_basket` | 3 | 0.723 | 29/17/4 | 2 | 0 |
| `place_object_scale` | 2 | 0.551 | 24/26 | 0 | 27 |
| `scan_object` | 3 | 0.242 | 20/29/1 | 10 | 35 |
| `blocks_ranking_rgb` | 4 | 0.325 | 8/16/12/14 | 19 | 33 |
| `hanging_mug` | 2 | 0.683 | 49/1 | 3 | 10 |
| `pick_diverse_bottles` | 4 | 0.140 | 13/19/6/12 | 26 | 27 |
| `place_cans_plasticbox` | 3 | 0.190 | 25/24/1 | 11 | 14 |
| `place_object_stand` | 2 | 0.603 | 29/21 | 3 | 29 |
| `shake_bottle` | 2 | 0.693 | 25/25 | 0 | 32 |
| `blocks_ranking_size` | 4 | 0.317 | 16/15/10/9 | 37 | 36 |
| `lift_pot` | 2 | 0.350 | 28/22 | 23 | 28 |
| `pick_dual_bottles` | 2 | 0.161 | 22/28 | 19 | 18 |
| `place_phone_stand` | 2 | 0.633 | 21/29 | 0 | 21 |
| `shake_bottle_horizontally` | 2 | 0.714 | 24/26 | 0 | 28 |
| `click_alarmclock` | 2 | 0.686 | 28/22 | 0 | 0 |
| `place_a2b_left` | 2 | 0.608 | 26/24 | 7 | 45 |
| `place_dual_shoes` | 4 | 0.172 | 8/10/11/21 | 30 | 29 |
| `place_shoe` | 2 | 0.592 | 31/19 | 1 | 28 |
| `stack_blocks_three` | 4 | 0.404 | 10/13/18/9 | 16 | 15 |
| `click_bell` | 2 | 0.703 | 31/19 | 0 | 16 |
| `place_a2b_right` | 3 | 0.654 | 16/32/2 | 8 | 55 |
| `place_empty_cup` | 2 | 0.655 | 27/23 | 2 | 9 |
| `stack_blocks_two` | 4 | 0.581 | 22/18/3/7 | 5 | 35 |
| `dump_bin_bigbin` | 2 | 0.671 | 22/28 | 0 | 12 |
| `move_playingcard_away` | 2 | 0.596 | 30/20 | 1 | 20 |
| `place_bread_basket` | 3 | 0.464 | 12/28/10 | 20 | 40 |
| `place_fan` | 2 | 0.604 | 27/23 | 3 | 29 |
| `put_bottles_dustbin` | 4 | 0.564 | 34/12/2/2 | 11 | 26 |
| `move_stapler_pad` | 2 | 0.559 | 28/22 | 3 | 19 |
| `place_bread_skillet` | 2 | 0.231 | 26/24 | 0 | 14 |
| `place_mouse_pad` | 2 | 0.576 | 31/19 | 1 | 25 |
| `put_object_cabinet` | 2 | 0.185 | 28/22 | 10 | 4 |
| `stack_bowls_two` | 4 | 0.549 | 13/13/20/4 | 10 | 27 |

## 5. 10 个 OOD 任务结果

| 任务 | K | Silhouette | 簇大小 | NN | CloseFar |
|---|---:|---:|---|---:|---:|
| `adjust_bottle` | 2 | 0.778 | 31/19 | 4 | 27 |
| `handover_block` | 4 | 0.272 | 24/15/2/9 | 30 | 35 |
| `open_microwave` | 4 | 0.462 | 26/17/1/6 | 4 | 0 |
| `turn_switch` | 2 | 0.573 | 27/23 | 20 | 18 |
| `place_container_plate` | 2 | 0.600 | 27/23 | 0 | 2 |
| `move_can_pot` | 3 | 0.706 | 29/19/2 | 4 | 25 |
| `move_pillbottle_pad` | 2 | 0.662 | 26/24 | 0 | 1 |
| `press_stapler` | 2 | 0.603 | 28/22 | 1 | 39 |
| `stack_bowls_three` | 4 | 0.370 | 10/14/13/13 | 22 | 30 |
| `grab_roller` | 2 | 0.252 | 21/29 | 12 | 17 |

## 6. 初步结论

### 6.1 优先候选

如果只根据当前 smoke test 进行下一轮 simulator 验证，优先级建议为：

1. `open_laptop`
2. `place_object_stand`
3. `place_bread_basket`
4. `stack_blocks_two`
5. `stack_bowls_two`

这些任务同时具备相对清晰的动作簇，以及一定数量的“初始画面相近但动作簇不同”候选。

### 6.2 备选任务

可以作为备选继续检查：

- `place_a2b_left`
- `place_shoe`
- `place_fan`
- `place_object_scale`
- `shake_bottle`

其中 `place_a2b_left` 的 CloseFar 较高，但左右目标语义可能直接决定动作，不一定能代表同一初始状态下的自由 action mode。

`shake_bottle` 和 `shake_bottle_horizontally` 的动作簇较清晰，但其任务成功条件相对简单，可能导致动作 mode 与真正的高质量行为不完全一致。

### 6.3 暂不优先的任务

`place_object_basket` 虽然动作 silhouette 较高，但 CloseFar 为 0，当前没有发现可靠的“初始画面近似相同、动作明显不同”证据。

带有大小为 1 或 2 的小簇的任务，例如 `hanging_mug`、`place_can_basket`、`scan_object`、`place_a2b_right`，需要先确认小簇不是噪声或异常轨迹，不能直接把这些簇当作正式 mode。

## 7. 对正式 Experiment 2A 的限制

本次结果不能直接证明原始数据中存在“相同 initial state 下的不同 mode”，原因是：

1. clean LeRobot parquet 中没有 simulator 物体初始位姿字段；
2. 首帧图像相似不等价于场景状态完全相同；
3. 动作簇可能主要反映左右臂选择，而不是更高层的策略 mode；
4. 原始 50 条 demonstration 的分布不等价于 No-WM/WM 采样分布。

正式 Experiment 2A 前，应从 RoboTwin simulator 的 episode seed、场景配置或原始轨迹恢复真实初始物体位姿，然后：

1. 按真实初始状态进行匹配或分层；
2. 在相同 fixed initial state 上分别采样 No-WM 和 WM；
3. 使用不包含模型来源和最终成功率的轨迹特征聚类；
4. 删除或单独标记样本量过小的 action cluster；
5. 再统计每个 mode 的概率和成功率。

