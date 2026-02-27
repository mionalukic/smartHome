import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";

@Injectable({
  providedIn: 'root'
})
export class DeviceStateService {

  constructor(private http: HttpClient) {}

  getCurrentState() {
    return this.http.get<any[]>('http://localhost:8080/api/state');
  }
}