import { Routes } from '@angular/router';
import { ShellComponent } from './layout/shell/shell';
import { DashboardComponent } from './pages/dashboard/dashboard';
import {SecurityComponent} from './security/security';
import {KitchenTimerComponent} from './pages/kitchen-timer/kitchen-timer';
import {CameraComponent} from './pages/camera/camera';

export const routes: Routes = [
  {
    path: '',
    component: ShellComponent,
    children: [
      {path :'security', component : SecurityComponent},
      {path: 'timer', component: KitchenTimerComponent},
      {path: 'camera', component: CameraComponent},
    ]
  }
];
