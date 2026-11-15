// Registers all chart.js controllers/scales for tree-shaken ng2-charts usage
import 'chart.js/auto';

import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch((err) => console.error(err));
