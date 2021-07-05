# -*- coding: utf-8; -*-

import ast
import re

from docutils.parsers.rst.directives.tables import CSVTable
from docutils.utils import SystemMessagePropagation


def non_negative_int(argument):
    """
    Converts the argument into an integer.
    Raises ValueError for negative or non-integer values.
    """
    value = int(argument)
    if value >= 0:
        return value
    else:
        raise ValueError('negative value defined; must be non-negative')


def non_negative_int_list(argument):
    """
    Converts a space- or comma-separated list of values into a Python list
    of integers.
    Raises ValueError for negative integer values.
    """
    if ',' in argument:
        entries = argument.split(',')
    else:
        entries = argument.split()
    return [non_negative_int(entry) for entry in entries]


class CSVFilterDirective(CSVTable):
    """ The CSV Filter directive renders csv defined in config
        and filter rows that contains a specified regex pattern
    """
    CSVTable.option_spec['include'] = ast.literal_eval
    CSVTable.option_spec['exclude'] = ast.literal_eval
    CSVTable.option_spec['included_cols'] = non_negative_int_list

    def parse_csv_data_into_rows(self, csv_data, dialect, source):
        rows, max_cols = super(
            CSVFilterDirective, self
        ).parse_csv_data_into_rows(csv_data, dialect, source)
        include_filters = list()
        exclude_filters = list()

        #Process include-filters
        if 'include' in self.options:
            for k, v in self.options['include'].items():
                if isinstance(v,list):
                    for vl in v:
                        include_filters.append({
                            k: re.compile(vl)
                        })
                elif isinstance(v,str):
                    include_filters.append({
                        k: re.compile(v)
                    })
                else:
                    error = self.state_machine.reporter.error(
                    f'Value of include index {k} is not string or list of strings'
                    )
                    raise SystemMessagePropagation(error)
        
        #Process exclude-filters
        if 'exclude' in self.options:
            for k, v in self.options['exclude'].items():
                if isinstance(v,list):
                    for vl in v:
                        exclude_filters.append({
                            k: re.compile(vl)
                        })
                elif isinstance(v,str):
                    exclude_filters.append({
                        k: re.compile(v)
                    })
                else:
                    error = self.state_machine.reporter.error(
                    f'Value of exclude index {k} is not string or list of strings'
                    )
                    raise SystemMessagePropagation(error)

        rows = self._apply_filters(rows, max_cols, include_filters, exclude_filters)
        
        #Process included cols
        if 'included_cols' in self.options:
            rows, max_cols = self._get_rows_with_included_cols(
                rows, self.options['included_cols']
            )
        return rows, max_cols

    def _apply_filters(self, rows, max_cols, include_filters, exclude_filters):
        result = []

        header_rows = self.options.get('header-rows', 0)
        # Always include header rows, if any
        result.extend(rows[:header_rows])

        for row in rows[header_rows:]:
            # We generally include a row, ...
            include = True
            if len(include_filters) > 0:
                # ... unless include filters are defined, then we generally
                # exclude them, ...
                include = False
                for inc_filters in include_filters:
                    for col_idx, pattern in inc_filters.items():
                        # cell data value is located at hardcoded index pos. 3
                        # data type is always a string literal
                        if max_cols - 1 >= col_idx:
                            if len(row[col_idx][3]) > 0 and pattern.search(row[col_idx][3][0]):
                                # ... unless at least one of the defined filters
                                # matches its cell ...
                                include = True
                                break
                       
            # ... unless exclude filters are defined (as well) ...
            if include and len(exclude_filters) > 0:
                for exc_filters in exclude_filters:
                    for col_idx, pattern in exc_filters.items():
                        # cell data value is located at hardcoded index pos. 3
                        # data type is always a string literal
                        if max_cols - 1 >= col_idx:
                            if len(row[col_idx][3]) > 0 and pattern.search(row[col_idx][3][0]):
                                # ... then we exclude a row if any of the defined
                                # exclude filters matches its cell.
                                include = False
                                break
                        
            
            if include:
                result.append(row)

        return result

    def _get_rows_with_included_cols(self, rows, included_cols_list):
        prepared_rows = []
        for row in rows:
            try:
                idx_row = [row[i] for i in included_cols_list]
                prepared_rows.append(idx_row)
            except IndexError:
                error = self.state_machine.reporter.error(
                    'One or more indexes of included_cols are not valid. '
                    'The CSV data does not contain that many columns.')
                raise SystemMessagePropagation(error)
        return prepared_rows, len(included_cols_list)


def setup(sphinx):
    sphinx.add_directive('csv-filter', CSVFilterDirective)
