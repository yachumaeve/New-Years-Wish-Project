import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { DonorPayload, WishItem } from '../models/type';

@Injectable({ providedIn: 'root' })
export class DataService {
  private apiUrl = '/api'; // 配合 Nginx 的反向代理路徑

  constructor(private http: HttpClient) {}

  // 1. 取得所有收件人資料 (GET /api/recipients)
  getRecipients(): Observable<WishItem[]> {
    // return throwError(() => new Error('伺服器炸掉啦！'));
    return this.http.get<WishItem[]>(`${this.apiUrl}/recipients`);
  }

  // 2. 儲存捐贈者資料 (POST /api/donors)
  submitDonation(payload: DonorPayload): Observable<any> {
    // return throwError(() => new Error('伺服器炸掉啦！'));
    return this.http.post(`${this.apiUrl}/donors`, payload);
  }
}