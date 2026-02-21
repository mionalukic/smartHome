import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SecurityService {

  private baseUrl = '/api';

  constructor(private http: HttpClient) {}

  getStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/security/status`);
  }

  arm(): Observable<any> {
    return this.http.post(`${this.baseUrl}/security/arm`, {});
  }

  disarm(): Observable<any> {
    return this.http.post(`${this.baseUrl}/security/disarm`, {});
  }

  alarmOff() {
    return this.http.post(`${this.baseUrl}/security/alarm/off`, {});
  }
  enterPin(key: string) {
    return this.http.post(`${this.baseUrl}/security/pin`, { key });
  }
}
