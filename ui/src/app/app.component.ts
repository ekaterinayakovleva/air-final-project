import {Component} from '@angular/core';
import {InferenceService} from './inference.service';
import {ImageData} from "./models";
import {HttpResponse} from "@angular/common/http";

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],
})
export class AppComponent {
    searchString: string = ''
    msgs = []
    blocks: ImageData[] = []

    constructor(private inferenceService: InferenceService) {
    }

    onSearch() {
        this.msgs = [];
        let ss = this.searchString.trim();
        if (ss === '') {
            this.msgs.push({severity: 'error', summary: 'Query is empty', detail: 'Please enter query into the field'});
            return;
        }

        this.inferenceService
            .getAlike(ss)
            .subscribe((response: HttpResponse<ImageData[]>) => {
                this.blocks = response.body.map(r => ({
                    url: r.url,
                    description: r.description
                }));
            }, (response: HttpResponse<ImageData[]>) => {
                this.blocks = []
                switch (response.status) {
                    case 404:
                        this.msgs.push({severity: 'warn', summary: 'Not found', detail: 'No images were found'});
                        break;
                    default:
                        this.msgs.push({
                            severity: 'error',
                            summary: 'Service down',
                            detail: 'Service is unavailable, try never'
                        });
                }
            })
    }
}
