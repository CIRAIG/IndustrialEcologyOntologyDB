import { Component } from '@angular/core';
import { EditableColumn, SmartTable, SmartTableCellChangePayload, SmartTableSortChangePayload } from '../../components/smart-table/smart-table';
import { of } from 'rxjs';
import { AclGraph, GraphModel } from '../../components/acl-graph/acl-graph';

@Component({
  selector: 'app-dashboard',
  imports: [SmartTable, AclGraph],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {

  MOCK_ACL_GRAPH: GraphModel = {
    nodes: [
      {
        id: 'process:p1',
        type: 'process',
        label: 'Steel production',
      },
      {
        id: 'process:p2',
        type: 'process',
        label: 'Car manufacturing',
      },
      {
        id: 'elem:el1',
        type: 'elementary_flow',
        label: 'CO₂ emissions',
      },
      {
        id: 'elem:el2',
        type: 'elementary_flow',
        label: 'Water consumption',
      },
    ],
  
    edges: [
      // Economic flow
      {
        id: 'edge:p1-p2',
        source: 'process:p1',
        target: 'process:p2',
      },
  
      // Elementary flow
      {
        id: 'edge:p1-el1',
        source: 'process:p1',
        target: 'elem:el1',
      },
      {
        id: 'edge:p1-el2',
        source: 'process:p1',
        target: 'elem:el2',
      },
    ],
  };


  columns: EditableColumn[] = [
    { key: 'uuid', header: 'UUID' },
    { key: 'name', header: 'Nom', inputType: 'text' },
    { key: 'age', header: 'Âge', inputType: 'number' },
    { key: 'role', header: 'Rôle', inputType: 'select', options: [{value: 'ADMIN', label: "Administrateur"}, {value: 'MEMBER', label: "Membre"}] },
    { key: 'autocomplete', header: 'Autocomplete', inputType: 'autocomplete', searchFunction: (query => this.autocompleteSearch(query)) }
  ];

  rows = [
    { uuid: 1, name: 'Alice', age: 28 },
    { uuid: 2, name: 'Bob', age: 34, role: 'ADMIN', autocomplete: { value: '2', label: 'Option 2' }},
  ];

  options = [
    {
      value: '1',
      label: 'Option 1'
    },
    {
      value: '2',
      label: 'Option 2'
    },
    {
      value: '3',
      label: 'Option 3'
    }
  ]

  sorting: SmartTableSortChangePayload | null = null;

  onCellChange(event: SmartTableCellChangePayload) {
    console.log('Cell changed', event);
    // you can sync to backend here
  }

  onSortChange(event: SmartTableSortChangePayload | null) {
    this.sorting = event;
  }

  autocompleteSearch(query: string) {
    return of(this.options.filter(option => option.label.toLowerCase().includes(query.toLowerCase())));
  }
 }
