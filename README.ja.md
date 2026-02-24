# Compare ThreadPoolExecutor and ProcessPoolExecutor

Pythonの標準ライブラリ `concurrent.futures` に含まれる `ThreadPoolExecutor` と `ProcessPoolExecutor` のパフォーマンスを比較するための実験用リポジトリです。

## 背景

現行のPython（CPython）には **GIL (Global Interpreter Lock)** が存在するため、マルチスレッド環境であっても、一度に1つのスレッドしかPythonバイトコードを実行できません。
python3.13から実験的にno-GIL(free-threading)の実装が開始されています。これも含めて実験を行います。

### **ThreadPoolExecutor (マルチスレッド):**
* 同じメモリ空間を共有するため軽量ですが、GILの影響を受けます。
* I/Oバウンドなタスク（通信待ちなど）には有効ですが、CPUバウンドなタスク（計算など）では並列化の恩恵を受けにくいです。
* 3.14-free-threadingであればGILの影響を受けないため,threadingが並列化の恩恵を受けられると思われます。


### **ProcessPoolExecutor (マルチプロセス):**
* 別のPythonインタープリタ（プロセス）を起動するため、それぞれが独自のGILを持ちます。
* CPUバウンドなタスクを複数のCPUコアに分散して並列実行できます。
* プロセス間の通信やメモリのコピーにオーバーヘッドが発生します。



## 実験内容

このプロジェクトでは、以下の2パターンのタスクを実行し、実行時間を比較します。

1. **CPU Bound Task:** 重い計算処理（例：大きなループ処理など）。
2. **Lock Free (can threadable) Task**: CネイティブコードなどでGIL無効(Python Objectを操作しない)．（例：numpy)


### 依存関係

* uv 0.9.x or abobe
* Python 3.x

## 実行方法

メインのスクリプトを実行して結果を確認します。

```bash
git clone https://github.com/tkuro11/compare_between_threadpool_and_processpool.git
cd compare_between_threadpool_and_processpool
uv sync
uv run comparison.py

```

## 結果の自動取得

以下のスクリプトで, python3.14(GIL), python3.14t(free-threading)を使った結果を results/ の下に取得します。
名前は [cpu brand]-python[version]-[GIL|free_thread].log となります。

```
uv run collect_results.py
```

## 結果のグラフ化

以下のコマンドで自動取得した結果をグラフ化します。
```bash
uv run graph_output_combine.py

```

## 結果の解釈（期待される挙動）

* **CPU Bound な処理の場合:**
* `ProcessPoolExecutor` の方が圧倒的に高速です。マルチコアを活用して並列に計算が行われるためです。
* `ThreadPoolExecutor` は、GILによるロックの競合が発生し、シングルスレッドでの実行と同等か、あるいはスレッド切り替えのオーバーヘッドにより遅くなる可能性があります。


* **Lock Free な処理の場合:**
* 両者ともに並列化の恩恵を受けられます。
* ただし、プロセスの起動コストがない分、`ThreadPoolExecutor` の方がわずかに効率的な場合が多いです。


* **free-threadingの効果:**
* CPU Boundな処理に置いては ThreadPoolExecutorがProcessPoolExecutorよりも良い結果を出す場合がありました。
* Lock Free (numpy) の場合、2threads/processesでは少しは向上が見られるものの、それ以上は増やすほど悪化する。
これはすでにnumpyでmulti threadingが行われておりover subscrptionの可能性、SIMD命令など最粒度での並列化も行われておりthread並列があまり効かないこと、numpy.sum()はほとんどMemory Boundであり、
むしろ連続走査による空間的局所性が失われ、キャッシュラインの再利用率が下がる。

## 結論

Pythonにおいて、計算資源をフルに活用する必要がある場合は **ProcessPool** を、通信などの待ち時間を効率化したい場合は **ThreadPool** を選択するのが一般的です。numpyのようにGIL をリリースする場合はThreadPoolも有効ですが，十分に並列化されているnumpyの場合，あまり大きな効果は得られまん．
