import {
  AfterViewInit,
  Component,
  ElementRef,
  Inject,
  Input,
  OnChanges,
  PLATFORM_ID,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import cytoscape, { Core, StylesheetJson } from 'cytoscape';
import dagre from 'dagre';
import cytoscapeDagre from 'cytoscape-dagre';
import { CommonModule, isPlatformBrowser } from '@angular/common';

cytoscape.use(cytoscapeDagre);

type NodeType = 'process' | 'economic_flow' | 'elementary_flow';

export interface GraphNode {
  id: string;
  type: NodeType;
  label: string;
  data?: any;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  data?: any;
}

export interface GraphModel {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

@Component({
  selector: 'app-acl-graph',
  imports: [CommonModule],
  templateUrl: './acl-graph.html',
  styleUrls: ['./acl-graph.scss'],
})
export class AclGraph implements AfterViewInit, OnChanges {
  @ViewChild('cyHost', { static: true }) cyHost!: ElementRef<HTMLDivElement>;

  @Input() graph!: GraphModel;

  private cy?: Core;

  constructor(@Inject(PLATFORM_ID) private platformId: object) {}

  ngAfterViewInit(): void {
    if (this.graph) this.initOrUpdate();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['graph'] && this.cyHost) {
      this.initOrUpdate();
    }
  }

  private initOrUpdate(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return; // SSR: do nothing
    }

    const elements = this.toCytoscapeElements(this.graph);

    if (!this.cy) {
      this.cy = cytoscape({
        container: this.cyHost.nativeElement,
        elements,
        style: this.styles(),
        layout: this.layout(),
        wheelSensitivity: 0.2,
      });

      // Example interactions:
      this.cy.on('tap', 'node', (evt) => {
        const node = evt.target;
        const payload = node.data('payload');
        // open side panel, modal, etc.
        console.log('node clicked', node.id(), payload);
      });

    } else {
      this.cy.elements().remove();
      this.cy.add(elements);
      this.cy.layout(this.layout()).run();
      this.cy.fit(undefined, 30);
    }
  }

  private toCytoscapeElements(graph: GraphModel) {
    const nodes = (graph?.nodes ?? []).map((n) => ({
      data: {
        id: n.id,
        label: n.label,
        type: n.type,
        payload: n.data ?? null,
      },
    }));

    const edges = (graph?.edges ?? []).map((e) => ({
      data: {
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label ?? '',
        payload: e.data ?? null,
      },
    }));

    return [...nodes, ...edges];
  }

  private layout() {
    return {
      name: 'dagre',
      rankDir: 'LR',     // Left-to-right
      nodeSep: 40,
      rankSep: 70,
      edgeSep: 10,
      animate: true,
      animationDuration: 200,
    };
  }
  
  private styles(): StylesheetJson {
    return [
      {
        selector: 'node',
        style: {
          shape: 'round-rectangle',
          label: 'data(label)',
          'text-wrap': 'wrap',
          'text-max-width': 140,
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': 11,
          padding: '10px',
          width: 'label',
          height: 'label',
          'border-width': 1,
          'border-color': '#cbd5e1',
          'background-color': '#ffffff',
        },
      },
      {
        selector: 'node[type = "process"]',
        style: {
          'border-color': '#60a5fa',
          'background-color': '#eff6ff',
        },
      },
      {
        selector: 'node[type = "economic_flow"]',
        style: {
          'border-color': '#34d399',
          'background-color': '#ecfdf5',
        },
      },
      {
        selector: 'node[type = "elementary_flow"]',
        style: {
          'border-color': '#fbbf24',
          'background-color': '#fffbeb',
          height: 7,
          'font-size': 5,
          padding: '2px',
        },
      },
      
      {
        selector: 'edge',
        style: {
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'arrow-scale': 1,
          'line-color': '#94a3b8',
          'target-arrow-color': '#94a3b8',
          width: 2,
          label: 'data(label)',
          'font-size': 10,
          'text-rotation': 'autorotate',
          'text-margin-y': -6,
        },
      },
    ] as StylesheetJson;
  }
  
}
