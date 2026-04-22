#!/usr/bin/env python3
"""
Automated SEO Enhancement for AI Tools Compare Website
Generates sitemap, analyzes SEO health, and prepares for affiliate integration
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class SEOAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.base_url = "https://huoxinjiang.github.io/ai-tools-compare/"
        self.html_files = []
        
    def discover_pages(self):
        """Discover all HTML pages in the build directory"""
        self.html_files = list(self.base_dir.glob('*.html'))
        # Filter out index.html from comparisons (it's handled separately)
        self.html_files = [f for f in self.html_files if f.suffix == '.html']
        print(f"🔍 Discovered {len(self.html_files)} HTML files")
        return self.html_files
    
    def extract_links(self, html_content):
        """Extract all internal links from HTML content"""
        pattern = r'href=["\']([^"\']+)["\']'
        return re.findall(pattern, html_content)
    
    def analyze_page(self, filepath):
        """Analyze SEO elements of a single page"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'file': filepath.name,
            'size': len(content),
            'title': None,
            'meta_description': None,
            'h1': None,
            'h2_count': 0,
            'internal_links': 0,
            'issues': []
        }
        
        # Extract title
        title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            analysis['title'] = title_match.group(1).strip()
            title_len = len(analysis['title'])
            if title_len < 30:
                analysis['issues'].append(f"Title too short ({title_len} chars, recommend 50-60)")
            elif title_len > 70:
                analysis['issues'].append(f"Title too long ({title_len} chars, recommend 50-60)")
        else:
            analysis['issues'].append("Missing <title> tag")
        
        # Extract meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content)
        if desc_match:
            desc = desc_match.group(1).strip()
            analysis['meta_description'] = desc
            desc_len = len(desc)
            if desc_len < 100:
                analysis['issues'].append(f"Description too short ({desc_len} chars, recommend 150-160)")
            elif desc_len > 200:
                analysis['issues'].append(f"Description too long ({desc_len} chars, recommend 150-160)")
        else:
            analysis['issues'].append("Missing meta description")
        
        # Extract H1
        h1_matches = re.findall(r'<h1[^>]*>([^<]+)</h1>', content)
        if h1_matches:
            analysis['h1'] = h1_matches[0].strip()
            if len(h1_matches) > 1:
                analysis['issues'].append(f"Multiple H1 tags found ({len(h1_matches)})")
        else:
            analysis['issues'].append("Missing H1 tag")
        
        # Count H2s
        analysis['h2_count'] = len(re.findall(r'<h2[^>]*>', content))
        
        # Count internal links
        links = self.extract_links(content)
        analysis['internal_links'] = len([l for l in links if l.startswith('/') or l.endswith('.html')])
        
        return analysis
    
    def generate_sitemap(self):
        """Generate sitemap.xml"""
        sitemap_urls = []
        today = datetime.now().strftime('%Y-%m-%d')
        
        for filepath in self.html_files:
            # Determine URL path
            if filepath.name == 'index.html':
                url = self.base_url
            else:
                url = self.base_url + filepath.name
            
            # Determine priority
            if filepath.name == 'index.html':
                priority = 1.0
            elif filepath.name.startswith('best-'):
                priority = 0.9
            elif 'cursor' in filepath.name or 'vscode' in filepath.name:
                priority = 0.8
            else:
                priority = 0.7
            
            sitemap_urls.append({
                'loc': url,
                'lastmod': today,
                'priority': priority,
                'changefreq': 'weekly' if priority >= 0.9 else 'monthly'
            })
        
        # Sort by priority (descending)
        sitemap_urls.sort(key=lambda x: x['priority'], reverse=True)
        
        # Generate sitemap XML
        sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
        
        for url_data in sitemap_urls:
            sitemap_xml += f"    <url>\n"
            sitemap_xml += f"        <loc>{url_data['loc']}</loc>\n"
            sitemap_xml += f"        <lastmod>{url_data['lastmod']}</lastmod>\n"
            sitemap_xml += f"        <priority>{url_data['priority']}</priority>\n"
            sitemap_xml += f"        <changefreq>{url_data['changefreq']}</changefreq>\n"
            sitemap_xml += f"    </url>\n"
        
        sitemap_xml += "</urlset>\n"
        
        # Write sitemap
        sitemap_path = self.base_dir / 'sitemap.xml'
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        
        print(f"✅ Generated sitemap with {len(sitemap_urls)} URLs")
        return sitemap_urls
    
    def generate_report(self):
        """Generate SEO analysis report"""
        print("\n" + "="*70)
        print("📊 SEO ANALYSIS REPORT")
        print("="*70)
        
        all_issues = 0
        pages_without_desc = 0
        pages_without_title = 0
        
        for filepath in self.html_files:
            analysis = self.analyze_page(filepath)
            
            print(f"\n📄 {analysis['file']} ({analysis['size']} bytes)")
            
            if analysis['title']:
                print(f"   Title: {analysis['title'][:60]}..." if len(analysis['title']) > 60 else f"   Title: {analysis['title']}")
            
            if analysis['meta_description']:
                print(f"   Description: {analysis['meta_description'][:60]}..." if len(analysis['meta_description']) > 60 else f"   Description: {analysis['meta_description']}")
            else:
                pages_without_desc += 1
            
            if analysis['h1']:
                print(f"   H1: {analysis['h1'][:50]}..." if len(analysis['h1']) > 50 else f"   H1: {analysis['h1']}")
            
            print(f"   H2s: {analysis['h2_count']}, Links: {analysis['internal_links']}")
            
            if analysis['issues']:
                all_issues += len(analysis['issues'])
                for issue in analysis['issues']:
                    print(f"   ⚠️  {issue}")
        
        print("\n" + "="*70)
        print(f"📈 SUMMARY:")
        print(f"   Total pages: {len(self.html_files)}")
        total_issues_str = f"   Total issues: {all_issues}"
        print(total_issues_str)
        print(f"   Pages missing description: {pages_without_desc}")
        print(f"   Pages missing title: {pages_without_title}")
        print("="*70)
        
        return {
            'total_pages': len(self.html_files),
            'total_issues': all_issues,
            'missing_description': pages_without_desc,
            'missing_title': pages_without_title
        }

def main():
    print("🚀 AI Tools Compare - SEO Enhancement Tool")
    print("="*70)
    
    # Initialize analyzer
    base_dir = Path('/Users/algea/workspace/AI-Tools-Compare')
    analyzer = SEOAnalyzer(base_dir)
    
    # Discover pages
    print("\n📂 Discovering pages...")
    analyzer.discover_pages()
    
    # Generate sitemap
    print("\n🗺️  Generating sitemap...")
    sitemap_urls = analyzer.generate_sitemap()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Save report as JSON
    report_path = base_dir / 'seo_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Report saved to {report_path}")
    
    return report

if __name__ == '__main__':
    main()
