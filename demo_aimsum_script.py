from importlib import reload
import traceback
import BuildMatrixFromPreDay

# force reloading the module in case the file has been modified
# Otherwise Aimsum will only load the module once for the application duration
reload(BuildMatrixFromPreDay)

print('Building...')
try:
	BuildMatrixFromPreDay.build(model)
except Exception as e:
	# pretty print exceptions because Aimsum doesn't
	for line in traceback.format_exc().split('\n'):
		print(line)
print('Done')
