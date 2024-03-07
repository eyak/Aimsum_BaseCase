# This is a blank aimsum script, 
# which should be created in Aimsum to use these functions

from importlib import reload
import BuildMatrixFromPreDay

# force reloading the module in case the file has been modified
# Otherwise Aimsum will only load the module once for the application duration
reload(BuildMatrixFromPreDay)

print('Building...')
BuildMatrixFromPreDay.build(model)
print('Done')
