import { NgModule } from '@angular/core';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { appRoutes } from './app.routes';
import { apolloProviders } from './core/apollo/apollo.config';
import { HttpInterceptor } from './core/interceptors/HttpInterceptor';

import { LayoutModule } from './layout/layout.module';
import { ComponentsModule } from './components/components.module';
import { PagesModule } from './core/pages/pages.module';

/**
 * Root module. The application shell (AppComponent) renders the layout and
 * a <router-outlet>; every routed page comes from PagesModule.
 */
@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(appRoutes),
    LayoutModule,
    ComponentsModule,
    PagesModule,
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: HttpInterceptor, multi: true },
    ...apolloProviders,
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
