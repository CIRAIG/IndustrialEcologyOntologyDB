import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { debounceTime, Observable, switchMap } from 'rxjs';


export interface EditableColumn {
  key: string;
  header: string;
  inputType?: 'text' | 'number' | 'select' | 'autocomplete';
  options?: any[]; // Used if inputType is 'select'
  searchFunction?: (query: string) => Observable<any[]>; // Used if inputType is 'autocomplete'
}

export interface SmartTableCellChangePayload {
  rowIndex: number | null;
  columnKey: string | null;
  value: any;
}

export interface SmartTableSortChangePayload {
  columnKey: string;
  order: 'ASC' | 'DESC';
}

@Component({
  selector: 'app-smart-table',
  imports: [CommonModule, FormsModule],
  templateUrl: './smart-table.html',
  styleUrl: './smart-table.scss',
})
export class SmartTable {
  @Input() columns: EditableColumn[] = [];
  @Input() rows: any[] = [];

  @Output() cellChange = new EventEmitter<SmartTableCellChangePayload>();
  @Output() sortChange = new EventEmitter<SmartTableSortChangePayload | null>();

  editing: SmartTableCellChangePayload = {
    rowIndex: null,
    columnKey: null,
    value: null
  };

  sorting: SmartTableSortChangePayload | null = null;

  colHovered: string | null = null;

  // Since autocomplete options are fetched asynchronously, we cache labels here
  // so that selected value can display its label immediately
  autocompleteLabelCache: { [key: string]: { [key: string]: string }} = {};

  constructor() {}

  isEditing(rowIndex: number, columnKey: string): boolean {
    return (
      this.editing.rowIndex === rowIndex &&
      this.editing.columnKey === columnKey
    );
  }

  startEdit(rowIndex: number, columnKey: string): void {
    if (this.columns.find(col => col.key === columnKey)?.inputType === undefined) {
      return; // Not editable
    }

    // Don’t restart if already editing that cell
    if (this.isEditing(rowIndex, columnKey)) return;

    this.editing = {
      rowIndex,
      columnKey,
      value: this.rows[rowIndex][columnKey]?.hasOwnProperty('value') ? this.rows[rowIndex][columnKey].value : this.rows[rowIndex][columnKey]
    };
  }

  saveEdit(): void {
    if (this.editing.rowIndex === null || this.editing.columnKey === null) {
      return;
    }

    const { rowIndex, columnKey, value } = this.editing;

    // Update data
    this.rows[rowIndex][columnKey] = value;

    // Emit event so parent can react / persist
    this.cellChange.emit({ rowIndex, columnKey, value });

    // Clear editing state
    this.editing = { rowIndex: null, columnKey: null, value: null };
  }

  cancelEdit(): void {
    this.editing = { rowIndex: null, columnKey: null, value: null };
  }

  onInputKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      event.preventDefault();
      this.saveEdit();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      this.cancelEdit();
    }
  }

  sortByColumn(columnKey: string): void {
    console.log('Sorting by column:', columnKey);
    if (this.sorting?.columnKey === columnKey && this.sorting.order === 'ASC') {
      this.sorting = { columnKey, order: 'DESC' };
    } else if (this.sorting?.columnKey === columnKey && this.sorting.order === 'DESC') {
      this.sorting = null;
    } else {
      this.sorting = { columnKey, order: 'ASC' };
    }

    this.sortChange.emit(this.sorting);
    return;
  }

  getSortIndicator(columnKey: string): string {
    if (this.colHovered === columnKey) {
      if (this.sorting?.columnKey === columnKey) {
        return this.sorting.order === 'ASC' ? '▼ (click to DESC)' : '(click to clear)';
      } else {
        return '▲ (click to ASC)';
      }    
    }

    if (this.sorting?.columnKey === columnKey) {
      return this.sorting.order === 'ASC' ? '▲' : '▼';
    }

    return '';
  }

  autocompleteOptions(columnKey: string): Observable<any[]> {
    const searchTerm = this.editing.value || '';
    console.log('Autocomplete search:', columnKey, searchTerm);
    const searchFunction = this.columns.find(col => col.key === columnKey)?.searchFunction;
    if (!searchFunction) {
      return new Observable<any[]>(); // Return an empty observable if searchFunction is undefined
    }
    return searchFunction(searchTerm).pipe(
      debounceTime(300),
      // Cache label for autocomplete
      switchMap(options => {
        options.forEach(option => {
          this.autocompleteLabelCache[columnKey] = this.autocompleteLabelCache[columnKey] || {};
          this.autocompleteLabelCache[columnKey][option.value] = option.label;
        });
        return new Observable<any[]>(observer => {
          observer.next(options);
          observer.complete();
        });
      })
    );
  }

  getLabelOfCell(row: any, column: EditableColumn): string {
    const value = row[column.key];
    if (row[column.key] && row[column.key].hasOwnProperty('label')) {
      return row[column.key].label;
    } else if (column.inputType === 'select' && column.options) {
      return this.getOptionLabel(column, value);
    } else if (column.inputType === 'autocomplete') {
      return this.getOptionLabelFromCache(column, value);
    } else {
      return value;
    }
  }

  getOptionLabel(column: EditableColumn, value: any): string {
    const option = column.options?.find(opt => opt.value === value);
    return option ? option.label : value;
  }

  getOptionLabelFromCache(column: EditableColumn, value: any): string {
    return this.autocompleteLabelCache[column.key]?.[value] || value;
  }
 }
