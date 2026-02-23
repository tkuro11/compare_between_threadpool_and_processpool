# Compare ThreadPoolExecutor and ProcessPoolExecutor

Pythonの標準ライブラリ `concurrent.futures` に含まれる `ThreadPoolExecutor` と `ProcessPoolExecutor` のパフォーマンスを比較するための実験用リポジトリです。

## 背景

Python（CPython）には **GIL (Global Interpreter Lock)** が存在するため、マルチスレッド環境であっても、一度に1つのスレッドしかPythonバイトコードを実行できません。

### **ThreadPoolExecutor (マルチスレッド):**
* 同じメモリ空間を共有するため軽量ですが、GILの影響を受けます。
* I/Oバウンドなタスク（通信待ちなど）には有効ですが、CPUバウンドなタスク（計算など）では並列化の恩恵を受けにくいです。


### **ProcessPoolExecutor (マルチプロセス):**
* 別のPythonインタープリタ（プロセス）を起動するため、それぞれが独自のGILを持ちます。
* CPUバウンドなタスクを複数のCPUコアに分散して並列実行できます。
* プロセス間の通信やメモリのコピーにオーバーヘッドが発生します。



## 実験内容

このプロジェクトでは、以下の2パターンのタスクを実行し、実行時間を比較します。

1. **CPU Bound Task:** 重い計算処理（例：大きなループ処理など）。
2. **Lock Free (can threadable) Task**: CネイティブコードなどでGIL無効(Python Objectを操作しない)．（例：numpy)

## 実行方法

### 依存関係

Python 3.x がインストールされている必要があります。
CPU利用率を出す場合はpsutilが必要です．

### 実行

メインのスクリプトを実行して結果を確認します。

```bash
python comparison.py

```

## 結果の解釈（期待される挙動）

* **CPU Bound な処理の場合:**
* `ProcessPoolExecutor` の方が圧倒的に高速です。マルチコアを活用して並列に計算が行われるためです。
* `ThreadPoolExecutor` は、GILによるロックの競合が発生し、シングルスレッドでの実行と同等か、あるいはスレッド切り替えのオーバーヘッドにより遅くなる可能性があります。


* **Lock Free な処理の場合:**
* 両者ともに並列化の恩恵を受けられます。
* ただし、プロセスの起動コストがない分、`ThreadPoolExecutor` の方がわずかに効率的な場合が多いです。



## 結論

Pythonにおいて、計算資源をフルに活用する必要がある場合は **ProcessPool** を、通信などの待ち時間を効率化したい場合は **ThreadPool** を選択するのが一般的です。numpyのようにGIL をリリースする場合はThreadPoolも有効ですが，十分に並列化されているnumpyの場合，あまり大きな効果は得られまん．
