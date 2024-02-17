# MultiParser
    
    import asyncio
    
    from MultiScraper import Parser, Manager
    from MultiScraper.type import Proxy, Service, Task, Request
    
    manager = Manager()
    manager.proxies.add(Proxy('HTTP', 'localhost'))
    manager.services.add(Service('site', 50))
    manager.services.add(Service('site2', 50))
    parser = Parser(manager)
    
    
    async def main():
        task1 = Task([Request('http://site.com', 'site') for _ in range(100)])
        task2 = Task([Request('http://site2.com', 'site2') for _ in range(100)])
        tasks = [task1, task2]
    
        await manager.run_manager()
    
        # Sequential execution, with Task 2 starting only after Task 1 completes
        for task in tasks:
            res = await parser.run_task(task)
            print(res)
    
        # or
    
        # Parallel execution, starting all tasks simultaneously.
        tasks = [parser.run_task(task) for task in tasks]
        for task in asyncio.as_completed(tasks):
            res = await task
            print(res)
    
    
    asyncio.run(main())
