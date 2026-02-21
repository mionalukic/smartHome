import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface KitchenTimerStatus {
  seconds: number;
  addN: number;
  blinking: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class KitchenService {

  private baseUrl = 'http://localhost:8080/api/kitchen/timer';

  constructor(private http: HttpClient) {}

  getStatus(): Observable<KitchenTimerStatus> {
    return this.http.get<KitchenTimerStatus>(`${this.baseUrl}/status`);
  }

  setTime(seconds: number) {
    return this.http.post(`${this.baseUrl}/time`, { seconds });
  }

  setAddN(n: number) {
    return this.http.post(`${this.baseUrl}/addN`, { n });
  }
}
