import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {BlockComponent} from './block/block.component';
import {ButtonModule, InputTextModule, MessageModule, MessageService, MessagesModule} from "primeng";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";

@NgModule({
    declarations: [
        AppComponent,
        BlockComponent
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        InputTextModule,
        ButtonModule,
        MessagesModule,
        MessageModule,
        BrowserAnimationsModule,
    ],
    providers: [MessageService],
    bootstrap: [AppComponent]
})
export class AppModule {
}
