from ganglia_runtime import GangliaRuntime

runtime = GangliaRuntime()
print(runtime.reason("Compare three options in a matrix.", operator="grid_game")["answer"])
