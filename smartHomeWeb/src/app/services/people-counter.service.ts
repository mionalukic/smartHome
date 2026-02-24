import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PeopleCounterService {

  private baseUrl = 'http://localhost:8080/api/people';

  constructor(private http: HttpClient) {}

  emptyRoom(room: string): Observable<Object> {
    console.log('poslao')
    return this.http.get(`${this.baseUrl}/${room}/exit-all`);
  }
}
