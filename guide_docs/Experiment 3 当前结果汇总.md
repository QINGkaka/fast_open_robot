# Experiment 3 当前结果汇总

更新时间：2026-09-29

下面汇总的是目前自己训练的 OpenWAM checkpoint 结果：

- No-WM：`clean40-action-only`
- WM：`clean40-wm-full`
- `x/y` 表示成功 episode 数 / 总 episode 数
- `-` 表示尚未运行

| Split | Task | Clean No-WM | Clean WM | Randomized No-WM | Randomized WM |
|---|---|---:|---:|---:|---:|
| Seen | Place Fan | 0/8 | 6/8 | - | - |
| Seen | Place A2B Right | 0/8 | 6/8 | - | - |
| Seen | Put Bottles Dustbin | 1/8 | 7/8 | - | - |
| Seen | Place Mouse Pad | 0/8 | 6/8 | - | - |
| Seen | Place Dual Shoes | 0/8 | 5/8 | - | - |
| Unseen | Adjust Bottle | 0/4 | 0/4 | 0/4 | 0/4 |
| Unseen | Grab Roller | 0/4 | 0/4 | 0/4 | 0/4 |
| Unseen | Place Container Plate | 2/4 | 2/4 | 2/4 | 1/4 |
| Unseen | Move Pillbottle Pad | - | - | - | - |
| Unseen | Move Can Pot | - | - | - | - |
| Unseen | Open Microwave | - | - | - | - |
| Unseen | Press Stapler | - | - | - | - |
| Unseen | Stack Bowls Three | - | - | - | - |
| Unseen | Handover Block | - | - | - | - |
| Unseen | Turn Switch | - | - | - | - |

## 聚合结果

`pp` 表示百分点（percentage points），即两个成功率的绝对差值。

| 实验象限 | 覆盖范围 | No-WM | WM | WM - No-WM |
|---|---|---:|---:|---:|
| Seen + Clean | 5 tasks x 8 eps | 1/40，2.5% | 30/40，75.0% | +72.5pp |
| Seen + Randomized | 未运行 | - | - | - |
| Unseen + Clean | 3 tasks x 4 eps | 2/12，16.7% | 2/12，16.7% | 0pp |
| Unseen + Randomized | 3 tasks x 4 eps | 2/12，16.7% | 1/12，8.3% | -8.3pp |

## 完整 Experiment 3 进度

若正式协议为每个 task、每个模型、每种环境跑 20 episodes：

| 象限 | 目标 Rollouts | 当前已有 | 完成度 |
|---|---:|---:|---:|
| Seen + Clean | 1,600 | 80 | 5.0% |
| Seen + Randomized | 1,600 | 0 | 0% |
| Unseen + Clean | 400 | 24 | 6.0% |
| Unseen + Randomized | 400 | 24 | 6.0% |
| **总计** | **4,000** | **128** | **3.2%** |

需要注意，当前已有数据的 episode 数分别是 8 和 4，并不是正式协议的 20。正式汇总时可以复用这些固定 seed 的结果，也可以统一生成 20-seed manifest 后重新运行；为了 protocol 整齐，后者更稳妥。
