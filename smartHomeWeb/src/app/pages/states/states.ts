import { Component, OnInit } from '@angular/core';
import { interval } from 'rxjs';
import { DeviceStateService } from './states.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-states',
  imports: [CommonModule],
  templateUrl: './states.html',
  styleUrl: './states.css',
})
export class States implements OnInit {

  states: any[] = [];

  constructor(private stateService: DeviceStateService) {}

  ngOnInit(): void {

    interval(2000).subscribe(() => {
      this.loadState();
    });

    this.loadState();
  }

  loadState() {
    this.stateService.getCurrentState()
      .subscribe(data => {
        this.states = data;
      });
  }
}
