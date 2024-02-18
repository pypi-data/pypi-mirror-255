

from mako.template import Template

def start (
	links,
	name_of_label = ""
):
	'''
	links = [
		{
			"path": "company/company.s.HTML",
			"name": "company/company"
		}
	]
	'''
	
	if (len (links) >= 1):
		open = links [0]['path']
	else:
		open = ""
	
	def make_links ():
		links_string = ""
		for link in links:
			path = link ['path']
			name = link ['name']
		
			links_string += (
				f'<a href="{ path }">{ name }</a>'
			)
			
		return links_string
		
	def make_select ():
		options = ""
		for link in links:
			path = link ['path']
			name = link ['name']
		
			options += (
				f'<option value="{ path }">{ name }</a>'
			)
			
		return """
			<select 
				id='link_selector'
				style='
					font-size: 1.2em;
				'
			>
		""" + options + "</select>"
		
	links_selector = make_select ()	
	links_string = make_links ()


	temp = Template ('''
<!doctype html>
<html lang="en">
<head>
	<meta charset="UTF-8" />
	<style>
	code {
		display: block;
		background: #EEE;
		padding: 10px;
		border-radius: 4px;
	}
	
	a {
		display: block;
	}
	

	</style>
</head>
<body 
	style="
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
	
		display: flex;
		flex-direction: column;
	
		margin: 0;
		padding: 0.2in; 
		
		font-size: 1.3em; 
		opacity: 0; 
		transition: opacity .5s;
	"
>
	<nav
		style="
			position: absolute;
			left: 0;
			top: 0;
		
			display: flex;
			justify-content: space-between;
			align-items: center;
			
			width: 100%;
			height: .75in;
			
			box-sizing: border-box;
			padding: 0 .25in;
			
			overflow: visible;
		"
	>
		<b>${ name_of_label }</b>			
		<div>${ links_selector }</div>
	</nav>
	<div 
		style="
			position: absolute;
			left: 0;
			top: .75in;
		
			width: 100%;
			height: calc(100% - .75in);
		
			box-sizing: border-box;
			padding: .2in;
			
		"
	>
		<iframe 
			id="statement"
			style="
				width: 100%;
				height: 100%;
				border: 0;
				
				opacity: 0;
				transition: opacity .1s;
				
				box-sizing: border-box;
				box-shadow: 0 0 9px 1px #bbb;
				border-radius: 6px;
			"
			src="${ open }" 
		></iframe>
	</div>

	<script>
		console.log ("lyrics");
		
		/*
					
		*/
		document.addEventListener ("DOMContentLoaded", function(event) { 
			document.body.style.opacity = 1;
			
			setTimeout (() => {		
				document.body.style.opacity = 1;
			}, 500)
		});	

		const $__statement = document.getElementById ("statement")

		link_selector = document.getElementById ("link_selector")
		console.log (link_selector)
		
		link_selector.addEventListener ("change", function (event) {
			console.log (event)
			$__statement.style.opacity = 0;
			
			setTimeout (() => {	
				$__statement.src = event.target.value
			}, 120);
			
			setTimeout (() => {	
				$__statement.style.opacity = 1;
			}, 140)
		})

		document.querySelectorAll ('a').forEach ($__link => {
			console.log ("for each", $__link)
			
			$__link.addEventListener ("click", function ($__event) {
				$__event.preventDefault ()
				$__statement.style.opacity = 0;
	
				// console.log (this.href)

				setTimeout (() => {	
					$__statement.src = this.href
				}, 120);
				
				setTimeout (() => {	
					$__statement.style.opacity = 1;
				}, 140)
			})
		})
		
		
		document.addEventListener ("DOMContentLoaded", function(event) { 
			$__statement.style.opacity = 1;
			setTimeout (() => {		
				$__statement.style.opacity = 1;
			}, 500)
		});	
	</script>
</body>
</html>
''')

	return temp.render (
		links_string = links_string,
		links_selector = links_selector,
		open = open,
		name_of_label = name_of_label
	)