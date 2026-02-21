import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';

import { KitchenService } from '../../services/kitchen.service';

@Component({
  selector: 'app-kitchen-timer',
  standalone: true,
  templateUrl: './kitchen-timer.html',
  styleUrls: ['./kitchen-timer.css'],
  imports: [
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatInputModule
  ]
})
export class KitchenTimerComponent implements OnInit {


  formSeconds: number | undefined;
  formAddN: number | undefined;

  constructor(private kitchen: KitchenService) {}

  ngOnInit() {
  }

 /* private loadStatus() {
    this.kitchen.getStatus().subscribe(data => {
      this.displaySeconds = data.seconds;
      this.blinking = data.blinking;
    });
  }*/

  updateTime() {
    if (this.formSeconds === undefined || this.formSeconds <= 0) {
      return;
    }

    const value = this.formSeconds;

    this.kitchen.setTime(value).subscribe(() => {
      this.formSeconds = undefined;   // reset
    });
  }

  updateAddN() {
    if (this.formAddN === undefined || this.formAddN <= 0) {
      return;
    }

    this.kitchen.setAddN(this.formAddN).subscribe(() => {
      this.formAddN = undefined;
    });
  }
}
