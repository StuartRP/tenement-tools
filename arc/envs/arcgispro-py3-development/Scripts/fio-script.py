
# -*- coding: utf-8 -*-
import re
import sys

from fiona.fio.main import main_group

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main_group())
