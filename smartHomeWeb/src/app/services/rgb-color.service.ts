import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RgbColorService {

  private baseUrl = 'http://localhost:8080/api/rgb';

  constructor(private http: HttpClient) {}

  changeColor(color: string): Observable<Object> {
    return this.http.post(`${this.baseUrl}/${color}`, {});
  }
}
