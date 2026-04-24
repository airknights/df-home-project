#!/usr/bin/env python3
import logging
import random
import sys

from df_home.llm_utils import ask_llm
from df_home.db_utils import query_db, handle_db_request

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(levelname)s]: %(message)s")

log = logging.getLogger(__name__)


def main():
    try:
        # guardrail: query db to get department and then set one at random
        data_rows = query_db("select distinct department from employee", return_data=True)
        data_rows_num_items = len(data_rows)
        if data_rows_num_items > 0:
            random_dept_index = random.randrange(1, data_rows_num_items)
        else:
            exit("No departments found. Exiting")

        department_selected = data_rows[random_dept_index][0]

        log.info(f"Selected department: {department_selected}")

        while True:
            line = input("You: ").strip()
            if not line:
                continue
            if line.lower().strip() in ("exit", "quit"):
                log.info("User requested exit.")
                break
            elif line.lower().startswith("ask_llm:"):
                ask_llm(line)
            else:
                handle_db_request(line, selected_department=department_selected)
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
