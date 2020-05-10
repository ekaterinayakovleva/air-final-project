import {Injectable} from '@angular/core';
import {HttpClient, HttpResponse} from '@angular/common/http';
import {Observable} from "rxjs";
import {ImageData} from "./models";
import {environment} from 'src/environments/environment';

@Injectable({
    providedIn: 'root'
})
export class InferenceService {

    constructor(private http: HttpClient) {
    }

    getAlike(searchString: string): Observable<HttpResponse<ImageData[]>> {
        return this.http.get<ImageData[]>(`${environment.inferenceUrl}/?query=${searchString}`, {observe: 'response'})
    }
}
